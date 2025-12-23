from fastapi import APIRouter, HTTPException, Depends, Query
from app.core.dependencies import db_dependency, user_dependency
from app.db.models.user import User
from app.db.models.conversation import Conversation
from app.db.models.form_template import FormTemplate
from app.db.models.field_template import FieldTemplate, FieldType
from app.db.models.form import Form
import logging

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = logging.getLogger(__name__)

@router.get("/users")
async def list_users(db = db_dependency):
	"""
	List all users
	"""
	logger.info("Admin requested list of all users.")
	users = db.query(User).all()
	return [
		{
			"id": user.id,
			"email": user.email,
			"firstname": user.firstname,
			"lastname": user.lastname
		} for user in users
	]

@router.delete("/users")
async def delete_user(
	email: str = Query(..., description="Email of the user to delete"), 
	db = db_dependency
):
	"""
	Delete a user given a user email
	"""
	logger.info(f"Admin requested deletion of user with email: {email}")
	user = db.query(User).filter(User.email == email).first()
	if not user:
		logger.warning(f"User with email {email} not found for deletion.")
		raise HTTPException(status_code=404, detail="User not found.")
	db.delete(user)
	db.commit()
	logger.info(f"User with email {email} deleted.")
	return {"detail": f"User {email} deleted."}

@router.get("/conversations")
async def list_conversations(db = db_dependency):
	"""
	List all conversations
	"""
	logger.info("Admin requested list of all conversations.")
	conversations = db.query(Conversation).all()
	return [
		{
			"id": conv.id,
			"title": conv.title,
			"user_id": conv.user_id,
			"form_id": conv.form_id,
			"created_at": conv.created_at,
			"updated_at": conv.updated_at
		} for conv in conversations
	]


@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: int, db = db_dependency):
	"""
	Get a conversation by ID.
	"""
	
	logger.info(f"Admin requested conversation with id {conversation_id}.")
	conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
	if not conv:
		logger.warning(f"Conversation with id {conversation_id} not found.")
		raise HTTPException(status_code=404, detail="Conversation not found.")
	return {
		"id": conv.id,
		"title": conv.title,
		"user_id": conv.user_id,
		"form_id": conv.form_id,
		"created_at": conv.created_at,
		"updated_at": conv.updated_at,
		"messages": [
			{
				"id": msg.id,
				"message_num": msg.message_num,
				"sender": msg.sender,
				"content": msg.content,
				"created_at": msg.created_at
			} for msg in conv.messages
		]
	}

# Get a form by id
@router.get("/form/{form_id}")
async def get_form(form_id: int, db = db_dependency):
	logger.info(f"Admin requested form with id {form_id}.")
	form = db.query(Form).filter(Form.id == form_id).first()
	if not form:
		logger.warning(f"Form with id {form_id} not found.")
		raise HTTPException(status_code=404, detail="Form not found.")
	return {
		"id": form.id,
		"firstname": form.firstname,
		"lastname": form.lastname,
		"user_id": form.user_id,
		"form_template_id": form.form_template_id,
		"created_at": form.created_at,
		"updated_at": form.updated_at,
		"published_at": form.published_at
	}

# 4. Create a form_template (no parameters)
@router.post("/form_templates")
async def create_form_template(db = db_dependency):
	logger.info("Admin requested creation of a new form_template.")
	form_template = FormTemplate()
	db.add(form_template)
	db.commit()
	db.refresh(form_template)
	logger.info(f"Created form_template with id {form_template.id}.")
	return {"id": form_template.id}

# ******NEEDS UPDATING******
@router.get("/form_templates/{form_template_id}")
async def get_form_template(form_template_id: int, db = db_dependency):
	"""
	Get a form_template by ID.
	"""
	logger.info(f"Admin request form_template with ID {form_template_id}.")
	form_template = db.query(FormTemplate).filter(FormTemplate.id == form_template_id).first()
	if not form_template:
		logger.warning(f"Form template with id {form_template_id} not found.")
		raise HTTPException(status_code=404, detail="Form not found.")
	return {
		"id": form_template.id,
		"created_at": form_template.created_at,
		"updated_at": form_template.updated_at,
		"field_templates": [
			{
				"id": ft.id,
				"name": ft.name,
				"field_type": ft.field_type,
				"description": ft.description,
				"created_at": ft.created_at,
				"updated_at": ft.updated_at
			} for ft in form_template.field_templates
		]
	}

@router.post("/field_templates")
async def create_field_template(
	form_template_id: int = Query(..., description="ID of form_template to attach field_template to"),
	name: str = Query(..., description="Field name"),
	field_type: FieldType = Query(..., description="Field type (string, integer, boolean, date, email, phone, address)"),
	description: str = Query(None, description="Field description"),
	db = db_dependency
):
	"""
	Create a field template and properly associate it
	with a form_template (indicated by ID)
	"""
	logger.info(f"Admin requested creation of field_template for form_template_id {form_template_id}.")
	form_template = db.query(FormTemplate).filter(FormTemplate.id == form_template_id).first()
	if not form_template:
		logger.warning(f"FormTemplate with id {form_template_id} not found.")
		raise HTTPException(status_code=404, detail="FormTemplate not found.")

	field_template = FieldTemplate(
		name=name,
		field_type=field_type,
		description=description,
		form_template_id=form_template_id
	)
	db.add(field_template)
	db.commit()
	db.refresh(field_template)
	logger.info(f"Created field_template with id {field_template.id} for form_template_id {form_template_id}.")
	return {"id": field_template.id}

@router.delete("/field_templates/{field_template_id}")
async def delete_field_template(field_template_id: int, db = db_dependency):
	logger.info(f"Admin requested deletion of field_template with id {field_template_id}.")
	field_template = db.query(FieldTemplate).filter(FieldTemplate.id == field_template_id).first()
	if not field_template:
		logger.warning(f"FieldTemplate with id {field_template_id} not found.")
		raise HTTPException(status_code=404, detail="FieldTemplate not found.")
	db.delete(field_template)
	db.commit()
	logger.info(f"Deleted field_template with id {field_template_id}.")
	return {"detail": "FieldTemplate deleted successfully.", "id": field_template_id}
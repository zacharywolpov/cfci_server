from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer
from app.core.dependencies import settings_dependency, openai_service_dependency, db_dependency, user_dependency
from app.db.models.field_submission import FieldSubmission
from app.db.models.form import Form
from app.db.models.message import Message
from app.db.models.conversation import Conversation
from app.schemas.chat_schemas import InitiateChatResponse, AdvanceChatRequest, AdvanceChatResponse
from app.schemas.openai_schemas import UpdateFormLLMOutput, DefaultLLMOutput
from app.utils.langgraph_utils import read_markdown_file
import logging

# Create router for all chat-related endpoints
router = APIRouter(
    prefix="/api/chat", 
    tags=["chat"]
)

# Configure logging
logger = logging.getLogger(__name__)


@router.post("/initiate")
async def initiate_chat(
    db = db_dependency,
    user = user_dependency
):
    """
    Endpoint to initiate a new chat session.
    """
    
    """
    1. Create new conversation entry in database
       with initial message and metadata.
    """
    init_message = """Hi! I'm an AI assistant here to help you with your questions about the Christenson
Family Center for Innovation. How can I assist you today?"""
    try:
        # Create new form record and link to conversation
        # IMPORTANT: Hard-coding form_template record with ID 1
        db_form = Form(
            user_id=user.id,
            form_template_id=1
        )
        db.add(db_form)
        db.commit()
        db.refresh(db_form)

        # Create new conv record
        db_conv = Conversation(
            title=f"CFCI x {user.firstname} {user.lastname} Chat",
            user_id=user.id,
            form_id=db_form.id
        )

        db.add(db_conv)
        db.commit()
        db.refresh(db_conv)
        logger.info(f"Conversation created with ID {db_conv.id} for user {user.id}.")
    except Exception as e:
        logger.error(f"Error creating conversation for user {user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation.")

    # # Create initial message from agent
    # try:
    #     db_message = Message(
    #         sender="agent",
    #         message_num=0,
    #         content=init_message,
    #         user_id=user.id,
    #         conversation_id=db_conv.id
    #     )
    #     db.add(db_message)
    #     db.commit()
    #     db.refresh(db_message)
    #     logger.info(f"Initial message added to conversation {db_conv.id} with message num {db_message.message_num} and system ID {db_message.id}.")
    # except Exception as e:
    #     logger.error(f"Error creating initial message for conversation {db_conv.id}: {e}")
    #     raise HTTPException(status_code=500, detail="Failed to create initial message.")

    """
    2. Return response with conversation and message details.
    """
    # response = InitiateChatResponse(
    #     conversation_id=db_conv.id,
    #     form_id=db_form.id,
    #     message_id=db_message.id,
    #     message_num=db_message.message_num,
    #     sender=db_message.sender,
    #     content=db_message.content
    # )
    response = InitiateChatResponse(
        conversation_id=db_conv.id,
        form_id=db_form.id
    )

    return response
    
@router.post("/advance")
async def advance_chat(
    payload: AdvanceChatRequest,
    request: Request,
    db = db_dependency,
    user = user_dependency,
    openai_service = openai_service_dependency
):
    """
    Main endpoint used to advance an existing conversation.

    1. Front-end will send user message here, along with the conversation
    ID to which it belongs.
    2. User message stored in database, and chat history + context
       retrieved for AI agent context.
    3. AI agent processes latest user message and generates next response:
        a. First processes user message to determine if any form fields
           need to be filled out or updated. Returns a list of fields that need
           to be updated with their new/added values.
        b. For any fields that need to be updated (i.e., already had values in
           the form but new information given), uses LLM calls to synthesize.
        c. Once form is updated, final LLM call generates the agent's next message,
           question, response, etc.
    """

    """
    1. Load conv from db, raise exception if conversation
       not found or malformed.
    """
    conv = db.query(Conversation).get(payload.conversation_id)
    if not conv or conv.user_id != user.id:
        logger.error(f"Conversation ID {payload.conversation_id} not found or does not belong to user {user.id}.")
        raise HTTPException(status_code=404, detail="Conversation not found.")

    """
    2. Add user's latest message to the db.
    """
    try:
        user_message = Message(
            sender="user",
            message_num=payload.message_step_num,
            content=payload.user_message,
            user_id=user.id,
            conversation_id=conv.id
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        logger.info(f"User message added to conversation {conv.id} with message num {user_message.message_num} and system ID {user_message.id}.")
    except Exception as e:
        logger.error(f"Fatal error adding user message to conversation {conv.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to add user message.")

    """
    3. Load the latest state of the conversation's form.
       Specifically, load:
        a.  The `form_template` record associated with the 
          conversation's form.
        b. All `field_submission` records associated with 
          the conversation's form.
       
       Then format context in the following format:
        ```### LATEST STATE OF THE FORM
           Field name: Business/Org Title
           Field data type: String
           Field instructions: The title of the business or org...
           Current value: NONE
           --
           Field name: Project Description
           Field data type: String
           Field instructions: A detailed description of the business's project...
           --
           ...
        ```
    """
    try:
        form = conv.form
        if not form:
            logger.warning(f"No form associated with conversation {conv.id}.")

        form_template = form.form_template if form else None
        if form_template == None:
            logger.warning(f"No form template associated with form {form.id if form else None} in conversation {conv.id}.")

        field_templates = form_template.field_templates if form_template else []
        if len(field_templates) == 0:
            logger.warning(f"No field templates associated with form template {form_template.id if form_template else None} in conversation {conv.id}.")

        field_submissions = [fs for fs in form.field_submissions] if form else []

        form_context: str = "### LATEST STATE OF THE FORM\n\n"

        for field_template in field_templates:
            submission = next((fs for fs in field_submissions if fs.field_template_id == field_template.id), None)
            form_context += f"Field name: {field_template.name}\n"
            form_context += f"Template field ID: {field_template.id}\n"
            form_context += f"Field data type: {field_template.field_type}\n"
            form_context += f"Field instructions: {field_template.description}\n"
            form_context += f"Current value: {submission.value if submission else 'NONE'}\n"
            form_context += "--\n"
        logger.info(f"Successfully loaded form context for conversation {conv.id}.")
    except Exception as e:
        logger.error(f"Fatal error loading form context for conversation {conv.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load form context.")
    
    """
    4. LLM CALL 1 - call first LLM with "update_form" prompt
       to make any necessary updates to the form.

       LLM will return in the following format:
        ```json
            {
                "fields_to_update": [
                    {
                        "type": "create" | "update",
                        "template_field_id": "abc123",
                        "field_name": "Business/Org Title",
                        "new_value": "New Title Here",
                        "confidence": 0.95,
                        "reasoning": "The user mentioned the new title explicitly..."
                    },
                    {
                        "type": "create" | "update",
                        "template_field_id": "def456",
                        "field_name": "Project Description",
                        "new_value": "Updated project description here.",
                        "confidence": 0.87,
                        "reasoning": "The user provided additional details about the project..."
                    },
                    ...
                ]
            }
        ```
    """
    try:
        # Load prompt template, fill in with form context
        prompt_template = read_markdown_file("app/prompts/update_form.md")
        full_prompt = prompt_template.replace("{{FORM_CONTEXT}}", form_context)

        # Fill in prompt with previous 10 messages in the conv (load
        # 20 for later usage)
        recent_messages = (
            db.query(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(Message.message_num.desc())
            .limit(20)
            .all()
        )
        recent_messages.reverse() # So oldest messages first

        recent_messages_llm1 = recent_messages[-10:]  # Last 10 messages for LLM 1

        for msg in recent_messages_llm1:
            role = "User" if msg.sender == "user" else "Agent"
            chat_history += f"{role}: {msg.content}\n"
        full_prompt = full_prompt.replace("{{CHAT_HISTORY}}", chat_history)
        logger.info(f"Successfully loaded and filled update_form prompt for conversation {conv.id}.")

        logger.info(f"FULL PROMPT LLM CALL 1: {full_prompt}")

        # Call LLM to get fields to update
        logger.info(f"LLM CALL 1 - calling LLM to update form for conversation {conv.id}.")
        llm_response = openai_service.handle_message(
            user_prompt=full_prompt,
            response_format=UpdateFormLLMOutput,
            system_prompt=""
        ).get("response")
        logger.info(f"LLM CALL 1 - received response from LLM to update form for conversation {conv.id}.")

        logger.info(f"LLM CALL 1 RESPONSE: {llm_response}")

    except Exception as e:
        logger.error(f"Fatal error during LLM call to update form for conversation {conv.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update form via LLM.")

    """
    5. Update fields in the database as necessary based on
       LLM response from step 4.
    """
    try:
        for field_update in llm_response.fields_to_update:
            if field_update.type == "create":
                # Create new FieldSubmission
                new_submission = FieldSubmission(
                    value=field_update.new_value,
                    llm_confidence=field_update.confidence,
                    status="DRAFT",
                    form_id=form.id,
                    field_template_id=field_update.template_field_id
                )
                db.add(new_submission)
                logger.info(f"Created new FieldSubmission for field {field_update.field_name} in conversation {conv.id}.")
            elif field_update.type == "update":
                # Update existing FieldSubmission.
                # Find from the list we loaded earlier.
                submission = next((fs for fs in form.field_submissions if fs.field_template_id == 
                                   field_update.template_field_id), None)
                if submission:
                    submission.value = field_update.new_value
                    submission.llm_confidence = field_update.confidence
                    submission.status = "FINAL"
                    db.add(submission)
                    logger.info(f"Updated FieldSubmission for field {field_update.field_name} in conversation {conv.id}.")
        db.commit()
        logger.info(f"Successfully updated form fields in database for conversation {conv.id}.")
    except Exception as e:
        logger.error(f"Fatal error updating form fields in database for conversation {conv.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update form fields in database.")

    """
    6. LLM CALL 2 - call second LLM with "generate_response" prompt
       to generate the agent's next message or question in the conversation.
    """
    # Rebuild form context after updates
    try:
        field_submissions = [fs for fs in form.field_submissions] if form else [] # Reload submissions
        form_context: str = "### LATEST STATE OF THE FORM\n\n"

        for field_template in field_templates:
            submission = next((fs for fs in field_submissions if fs.field_template_id == field_template.id), None)
            form_context += f"Field name: {field_template.name}\n"
            form_context += f"Field data type: {field_template.field_type}\n"
            form_context += f"Field instructions: {field_template.description}\n"
            form_context += f"Current value: {submission.value if submission else 'NONE'}\n"
            form_context += "--\n"
        logger.info(f"Successfully rebuilt form context for conversation {conv.id} after updates.")
    except Exception as e:
        logger.error(f"Fatal error rebuilding form context for conversation {conv.id} after updates: {e}")
        raise HTTPException(status_code=500, detail="Failed to rebuild form context.")
    
    # Load prompt template, fill in with form context and recent chat history,
    # make LLM call
    try:
        prompt_template = read_markdown_file("app/prompts/generate_response.md")
        full_prompt = prompt_template.replace("{{FORM_CONTEXT}}", form_context)

        # Fill in prompt with previous 30 messages in the conv
        chat_history = ""
        for msg in recent_messages:
            role = "User" if msg.sender == "user" else "Agent"
            chat_history += f"{role}: {msg.content}\n"
        full_prompt = full_prompt.replace("{{CHAT_HISTORY}}", chat_history)
        full_prompt = full_prompt.replace("{{LATEST_MESSAGE}}", user_message.content)
        logger.info(f"Successfully loaded and filled generate_response prompt for conversation {conv.id}.")

        # Call LLM to get agent's next message
        logger.info(f"LLM CALL 2 - calling LLM to generate agent response for conversation {conv.id}.")
        llm_response = openai_service.handle_message(
            user_prompt=full_prompt,
            response_format=DefaultLLMOutput,
            system_prompt=""
        ).get("response")
        logger.info(f"LLM CALL 2 - received response from LLM to generate agent response for conversation {conv.id}.")
    except Exception as e:
        logger.error(f"Fatal error during LLM call to generate agent response for conversation {conv.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate agent response via LLM.")
    


    """
    7. Load agent's next message into the DB,
       return response with agent's message details.
    """
    try:
        agent_message = Message(
            sender="agent",
            message_num=user_message.message_num + 1,
            content=llm_response.output_text,
            user_id=user.id,
            conversation_id=conv.id
        )
        db.add(agent_message)
        db.commit()
        db.refresh(agent_message)
        logger.info(f"Agent message added to conversation {conv.id} with message num {agent_message.message_num} and system ID {agent_message.id}.")
    except Exception as e:
        logger.error(f"Fatal error adding agent message to conversation {conv.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to add agent message.")
    
    return AdvanceChatResponse(
        message_id=agent_message.id,
        message_num=agent_message.message_num,
        sender=agent_message.sender,
        content=agent_message.content
    )
"""SQLAdmin configuration and model views for database administration"""

from sqladmin import Admin, ModelView

from app.database import engine
from app.models import Conversation, LeadData, Message, PTPreferences


class ConversationAdmin(ModelView, model=Conversation):
    """Admin view for Conversation model"""

    name = "Conversation"
    name_plural = "Conversations"
    icon = "fa-solid fa-comments"

    # List view configuration
    column_list = [
        Conversation.id,
        Conversation.phone_number,
        Conversation.status,
        Conversation.pt_id,
        Conversation.created_at,
        Conversation.updated_at,
    ]
    column_searchable_list = [Conversation.phone_number]
    column_sortable_list = [
        Conversation.id,
        Conversation.phone_number,
        Conversation.status,
        Conversation.created_at,
    ]
    column_default_sort = [(Conversation.created_at, True)]

    # Detail view configuration
    column_details_list = [
        Conversation.id,
        Conversation.phone_number,
        Conversation.status,
        Conversation.pt_id,
        Conversation.created_at,
        Conversation.updated_at,
    ]

    # Form configuration
    form_columns = [
        Conversation.phone_number,
        Conversation.status,
        Conversation.pt_id,
    ]


class MessageAdmin(ModelView, model=Message):
    """Admin view for Message model"""

    name = "Message"
    name_plural = "Messages"
    icon = "fa-solid fa-message"

    # List view configuration
    column_list = [
        Message.id,
        Message.conversation_id,
        Message.role,
        Message.content,
        Message.timestamp,
    ]
    column_searchable_list = [Message.content]
    column_sortable_list = [
        Message.id,
        Message.conversation_id,
        Message.timestamp,
        Message.role,
    ]
    column_default_sort = [(Message.timestamp, True)]

    # Detail view configuration
    column_details_list = [
        Message.id,
        Message.conversation_id,
        Message.role,
        Message.content,
        Message.timestamp,
        Message.twilio_message_sid,
    ]

    # Form configuration
    form_columns = [
        Message.conversation_id,
        Message.role,
        Message.content,
        Message.twilio_message_sid,
    ]


class LeadDataAdmin(ModelView, model=LeadData):
    """Admin view for LeadData model"""

    name = "Lead"
    name_plural = "Leads"
    icon = "fa-solid fa-user"

    # List view configuration
    column_list = [
        LeadData.id,
        LeadData.conversation_id,
        LeadData.goals,
        LeadData.age,
        LeadData.location,
        LeadData.budget_range,
        LeadData.commitment_level,
        LeadData.qualification_score,
        LeadData.is_qualified,
    ]
    column_searchable_list = [LeadData.goals, LeadData.location]
    column_sortable_list = [
        LeadData.id,
        LeadData.qualification_score,
        LeadData.age,
        LeadData.is_qualified,
    ]
    column_default_sort = [(LeadData.id, True)]

    # Detail view configuration
    column_details_list = [
        LeadData.id,
        LeadData.conversation_id,
        LeadData.goals,
        LeadData.age,
        LeadData.location,
        LeadData.budget_range,
        LeadData.commitment_level,
        LeadData.availability,
        LeadData.qualification_score,
        LeadData.is_qualified,
        LeadData.reasoning,
    ]

    # Form configuration
    form_columns = [
        LeadData.conversation_id,
        LeadData.goals,
        LeadData.age,
        LeadData.location,
        LeadData.budget_range,
        LeadData.commitment_level,
        LeadData.availability,
        LeadData.qualification_score,
        LeadData.is_qualified,
        LeadData.reasoning,
    ]


class PTPreferencesAdmin(ModelView, model=PTPreferences):
    """Admin view for PTPreferences model"""

    name = "PT Preference"
    name_plural = "PT Preferences"
    icon = "fa-solid fa-gear"

    # List view configuration
    column_list = [
        PTPreferences.id,
        PTPreferences.name,
        PTPreferences.specialty,
        PTPreferences.preferred_location,
        PTPreferences.min_budget,
        PTPreferences.required_commitment,
    ]
    column_searchable_list = [PTPreferences.name, PTPreferences.specialty]
    column_sortable_list = [PTPreferences.id, PTPreferences.name]

    # Detail view configuration
    column_details_list = [
        PTPreferences.id,
        PTPreferences.name,
        PTPreferences.bio,
        PTPreferences.specialty,
        PTPreferences.target_goals,
        PTPreferences.age_range,
        PTPreferences.preferred_location,
        PTPreferences.min_budget,
        PTPreferences.required_commitment,
        PTPreferences.years_experience,
        PTPreferences.certifications,
        PTPreferences.additional_info,
        PTPreferences.discovery_prompt_override,
        PTPreferences.qualification_prompt_override,
        PTPreferences.rejection_email_override,
        PTPreferences.booking_confirmation_override,
        PTPreferences.prompt_version,
        PTPreferences.prompts_last_updated,
    ]

    # Form configuration
    form_columns = [
        PTPreferences.name,
        PTPreferences.bio,
        PTPreferences.specialty,
        PTPreferences.target_goals,
        PTPreferences.age_range,
        PTPreferences.preferred_location,
        PTPreferences.min_budget,
        PTPreferences.required_commitment,
        PTPreferences.years_experience,
        PTPreferences.certifications,
        PTPreferences.additional_info,
        PTPreferences.discovery_prompt_override,
        PTPreferences.qualification_prompt_override,
        PTPreferences.rejection_email_override,
        PTPreferences.booking_confirmation_override,
        PTPreferences.prompt_version,
    ]


def setup_admin(app) -> Admin:
    """Initialize and configure SQLAdmin for the FastAPI application"""
    admin = Admin(app, engine, title="PT Lead Qualification Admin")

    # Register model views
    admin.add_view(ConversationAdmin)
    admin.add_view(MessageAdmin)
    admin.add_view(LeadDataAdmin)
    admin.add_view(PTPreferencesAdmin)

    return admin
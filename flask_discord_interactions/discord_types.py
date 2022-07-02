from typing import Optional, Union, List, Literal
from dataclasses import dataclass
import enum

# TODO: Should this be an actual type instead of just an alias for str?
Snowflake = str

class InteractionType(enum.IntEnum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5

class InteractionCallbackType(enum.IntEnum):
    PONG = 1 #	ACK a Ping
    CHANNEL_MESSAGE_WITH_SOURCE = 4 #	respond to an interaction with a message
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5 #	ACK an interaction and edit a response later, the user sees a loading state
    DEFERRED_UPDATE_MESSAGE = 6 #	for components, ACK an interaction and edit the original message later; the user does not see a loading state
    UPDATE_MESSAGE = 7 #	for components, edit the message the component was attached to
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8 #	respond to an autocomplete interaction with suggested choices
    MODAL = 9 #	respond to an interaction with a popup modal

class CommandType(enum.IntEnum):
    CHAT = 1
    USER = 2
    MESSAGE = 3

class ApplicationCommandOptionType(enum.IntEnum):
    SUB_COMMAND = 1 #	
    SUB_COMMAND_GROUP = 2 #	
    STRING = 3 #	
    INTEGER = 4 #	Any integer between -2^53 and 2^53
    BOOLEAN = 5 #	
    USER = 6 #	
    CHANNEL = 7 #	Includes all channel types + categories
    ROLE = 8 #	
    MENTIONABLE = 9 #	Includes users and roles
    NUMBER = 10 #	Any double between -2^53 and 2^53
    ATTACHMENT = 11 #	attachment object

class ChannelType(enum.IntEnum):
    GUILD_TEXT = 0 #	a text channel within a server
    DM = 1 #	a direct message between users
    GUILD_VOICE = 2 #	a voice channel within a server
    GROUP_DM = 3 #	a direct message between multiple users
    GUILD_CATEGORY = 4 #	an organizational category that contains up to 50 channels
    GUILD_NEWS = 5 #	a channel that users can follow and crosspost into their own server
    GUILD_NEWS_THREAD = 10 #	a temporary sub-channel within a GUILD_NEWS channel
    GUILD_PUBLIC_THREAD = 11 #	a temporary sub-channel within a GUILD_TEXT channel
    GUILD_PRIVATE_THREAD = 12 #	a temporary sub-channel within a GUILD_TEXT channel that is only viewable by those invited and those with the MANAGE_THREADS permission
    GUILD_STAGE_VOICE = 13 #	a voice channel for hosting events with an audience
    GUILD_DIRECTORY = 14 #	the channel in a hub containing the listed servers
    GUILD_FORUM = 15 #	(still in development) a channel that can only contain threads

class ComponentType(enum.IntEnum):
    ACTION_ROW = 1 # A container for other components
    BUTTON = 2 # A button object
    SELECT_MENU = 3 # A select menu for picking from choices
    TEXT_INPUT = 4 # A text input object

class ButtonStyle(enum.IntEnum):
    PRIMARY = 1 # 	blurple	custom_id
    SECONDARY = 2 # 	grey	custom_id
    SUCCESS = 3 # 	green	custom_id
    DANGER = 4 # 	red	custom_id
    LINK = 5 # 	grey, navigates to a URL	url

class TextInputStyle(enum.IntEnum):
    SHORT = 1	# A single-line input
    PARAGRAPH = 2 # A multi-line input

class MessageFlags(enum.IntEnum):
    CROSSPOSTED = 1 << 0 # this message has been published to subscribed channels (via Channel Following)
    IS_CROSSPOST = 1 << 1 # this message originated from a message in another channel (via Channel Following)
    SUPPRESS_EMBEDS = 1 << 2 # do not include any embeds when serializing this message
    SOURCE_MESSAGE_DELETED = 1 << 3 # the source message for this crosspost has been deleted (via Channel Following)
    URGENT = 1 << 4 # this message came from the urgent message system
    HAS_THREAD = 1 << 5 # this message has an associated thread, with the same id as the message
    EPHEMERAL = 1 << 6 # this message is only visible to the user who invoked the Interaction
    LOADING = 1 << 7 # this message is an Interaction Response and the bot is "thinking"
    FAILED_TO_MENTION_SOME_ROLES_IN_THREAD = 1 << 8 # this message failed to mention some roles and add their members to the thread


# TODO :s/dict/RealType/g

@dataclass
class Emoji:
    id: Snowflake # snowflake	emoji id
    name: str # string (can be null only in reaction emoji objects)	emoji name
    roles: Optional[List[Snowflake]] # array of role object ids	roles allowed to use this emoji
    user: Optional[dict] # user object	user that created this emoji
    require_colons: Optional[bool] # boolean	whether this emoji must be wrapped in colons
    managed: Optional[bool] # boolean	whether this emoji is managed
    animated: Optional[bool] # boolean	whether this emoji is animated
    available: Optional[bool] # boolean	whether this emoji can be used, may be false due to loss of Server Boosts


@dataclass
class ApplicationCommandOptionChoice:
    name: str # string	1-100 character choice name
    value: Union[str, int, float] # string, integer, or double *	Value for the choice, up to 100 characters if string
    name_localizations: Optional[dict] = None # dictionary with keys in available locales	Localization dictionary for the name field. Values follow the same restrictions as name

@dataclass
class Resolved:
    users: Optional[dict] = None # Map of Snowflakes to user objects	the ids and User objects
    members: Optional[dict] = None # Map of Snowflakes to partial member objects	the ids and partial Member objects
    roles: Optional[dict] = None # Map of Snowflakes to role objects	the ids and Role objects
    channels: Optional[dict] = None # Map of Snowflakes to partial channel objects	the ids and partial Channel objects
    messages: Optional[dict] = None # Map of Snowflakes to partial messages objects	the ids and partial Message objects
    attachments: Optional[dict] = None # Map of Snowflakes to attachment objects	the ids and attachment objects

@dataclass
class ApplicationCommandInteractionDataOption:
    name: str # string	Name of the parameter
    type: ApplicationCommandOptionType # integer	Value of application command option type
    value: Optional[Union[str, int, float]] = None # string, integer, or double	Value of the option resulting from user input
    options: Optional[List['ApplicationCommandInteractionDataOption']] = None # array of application command interaction data option	Present if this option is a group or subcommand
    focused: Optional[bool] = None # boolean	true if this option is the currently focused option for autocomplete

@dataclass
class ApplicationCommandOption:
    type: ApplicationCommandOptionType # one of application command option type	Type of option
    name: str # string	1-32 character name
    description: str = "" # string	1-100 character description
    name_localizations: Optional[dict] = None # dictionary with keys in available locales	Localization dictionary for the name field. Values follow the same restrictions as name
    description_localizations: Optional[dict] = None # dictionary with keys in available locales	Localization dictionary for the description field. Values follow the same restrictions as description
    required: Optional[bool] = None # boolean	If the parameter is required or optional--default false
    choices: Optional[List[ApplicationCommandOptionChoice]] = None # array of application command option choice	Choices for STRING, INTEGER, and NUMBER types for the user to pick from, max 25
    options: Optional[List['ApplicationCommandOption']] = None # array of application command option	If the option is a subcommand or subcommand group type, these nested options will be the parameters
    channel_types: Optional[List[ChannelType]] = None # array of channel types	If the option is a channel type, the channels shown will be restricted to these types
    min_value: Optional[Union[int, float]] = None # integer for INTEGER options, double for NUMBER options	If the option is an INTEGER or NUMBER type, the minimum value permitted
    max_value: Optional[Union[int, float]] = None # integer for INTEGER options, double for NUMBER options	If the option is an INTEGER or NUMBER type, the maximum value permitted
    autocomplete: Optional[bool] = None # boolean	If autocomplete interactions are enabled for this STRING, INTEGER, or NUMBER type option

@dataclass
class InteractionData:
    id: Snowflake # snowflake	the ID of the invoked command
    name: str # string	the name of the invoked command
    type: CommandType # integer	the type of the invoked command
    resolved: Optional[Resolved] = None # resolved data	converted users + roles + channels + attachments
    options: Optional[List[ApplicationCommandInteractionDataOption]] = None # array of application command interaction data option	the params + values from the user
    guild_id: Optional[str] = None # snowflake	the id of the guild the command is registered to
    target_id: Optional[str] = None # snowflake	id of the user or message targeted by a user or message command

# TODO: These can have their own definition
# FIXME: I think these are treated as aliases
ChatData = InteractionData
UserData = InteractionData
MessageData = InteractionData
# If we do give them their own definition
# InteractionData = Union[ChatData, UserData, MessageData]

# TODO: dedicated type for snowflakes?

@dataclass
class Interaction:
    id: Snowflake #	snowflake	ID of the interaction
    application_id: Snowflake #	snowflake	ID of the application this interaction is for
    type: InteractionType #	interaction type	Type of interaction
    token: str #	string	Continuation token for responding to the interaction
    version: int #	integer	Read-only property, always 1
    guild_id: Optional[Snowflake] = None #	snowflake	Guild that the interaction was sent from
    channel_id: Optional[Snowflake] = None #	snowflake	Channel that the interaction was sent from
    member: Optional[dict] = None #	guild member object	Guild member data for the invoking user, including permissions
    user: Optional[dict] = None #	user object	User object for the invoking user, if invoked in a DM
    message: Optional[dict] = None #	message object	For components, the message they were attached to
    app_permissions: Optional[str] = None #	string	Bitwise set of permissions the app or bot has within the channel the interaction was sent from
    locale: Optional[str] = None #	string	Selected language of the invoking user
    guild_locale: Optional[str] = None# 	Guild's preferred locale, if invoked in a guild
    # Expected to be overridden in child classes
    data: Optional[dict] = None #	interaction data	Interaction data payload

@dataclass
class ChatInteraction(Interaction):
    data: ChatData

@dataclass
class UserInteraction(Interaction):
    data: UserData

@dataclass
class MessageInteraction(Interaction):
    data: MessageData

CommandInteraction = Union[ChatInteraction, UserInteraction, MessageInteraction]

@dataclass
class SelectOption:
    label: str # string	the user-facing name of the option, max 100 characters
    value: str # string	the dev-defined value of the option, max 100 characters
    description: Optional[str] # string	an additional description of the option, max 100 characters
    emoji: Optional[Emoji] # partial emoji object	id, name, and animated
    default: Optional[bool] # boolean	will render this option as selected by default

@dataclass
class MessageComponent:
    custom_id: str # string	the custom_id of the component
    component_type: int # integer	the type of the component
    values: List[SelectOption] # array of select option values	values the user selected in a select menu component

@dataclass
class ModalSubmit:
    custom_id: str # string	the custom_id of the modal
    components: List[MessageComponent] # array of message components	the values submitted by the user

# This is sent on the message object when the message is a response to an Interaction without an existing message.
# TODO: WTF does the above sentence mean?
# @dataclass
# class MessageInteraction:
#     id: Snowflake # snowflake	ID of the interaction
#     type: InteractionType # interaction type	Type of interaction
#     name: str # string	Name of the application command, including subcommands and subcommand groups
#     user: str # user object	User who invoked the interaction
#     member: Optional[dict] # partial member object	Member who invoked the interaction in the guild

# TODO: Components
# Should the type: Literal[...] properties default to their thing?
# Should the type: Literal[...] properties just not exist?
# How does jsons deal with polymorphism? If I had to guess it doesn't, it almost can't

@dataclass
class ActionRow:
    # TODO
    pass

@dataclass
class Button:
    type: Literal[ComponentType.BUTTON] # integer	2 for a button
    style: ButtonStyle # integer	one of button styles
    label: Optional[str] = None # string	text that appears on the button, max 80 characters
    emoji: Optional[Emoji] = None # partial emoji	name, id, and animated
    custom_id: Optional[str] = None # string	a developer-defined identifier for the button, max 100 characters
    url: Optional[str] = None # string	a url for link-style buttons
    disabled: bool = False # boolean	whether the button is disabled (default false)

@dataclass
class SelectMenu:
    type: Literal[ComponentType.SELECT_MENU] # integer	3 for a select menu
    custom_id: str # string	a developer-defined identifier for the select menu, max 100 characters
    options: List[SelectOption] # array of select options	the choices in the select, max 25
    placeholder: Optional[str] = None # string	custom placeholder text if nothing is selected, max 150 characters
    min_values: Optional[int] = None # integer	the minimum number of items that must be chosen; default 1, min 0, max 25
    max_values: Optional[int] = None # integer	the maximum number of items that can be chosen; default 1, max 25
    disabled: bool = False # boolean	disable the select, default false

@dataclass
class TextInput:
    type: Literal[ComponentType.TEXT_INPUT] # integer	4 for a text input
    custom_id: str # string	a developer-defined identifier for the input, max 100 characters
    style: TextInputStyle # integer	the Text Input Style
    label: str # string	the label for this component, max 45 characters
    min_length: Optional[int] = None # integer	the minimum input length for a text input, min 0, max 4000
    max_length: Optional[int] = None # integer	the maximum input length for a text input, min 1, max 4000
    required: bool = True # boolean	whether this component is required to be filled, default true
    value: Optional[str] = None # string	a pre-filled value for this component, max 4000 characters
    placeholder: Optional[str] = None # string	custom placeholder text if the input is empty, max 100 characters

Component = Union[ActionRow, Button, SelectMenu, TextInput]


@dataclass
class InteractionCallbackDataMessages:
    tts: Optional[bool] = None # boolean	is the response TTS
    content: Optional[str] = None # string	message content
    embeds: Optional[List[dict]] = None # array of embeds	supports up to 10 embeds
    allowed_mentions: Optional[dict] = None # allowed mentions	allowed mentions object
    flags: Optional[int] = None # integer	message flags combined as a bitfield (only SUPPRESS_EMBEDS and EPHEMERAL can be set)
    components: Optional[List[Component]] = None # array of components	message components
    attachments: Optional[List[dict]] = None # array of partial attachment objects	attachment objects with filename and description


@dataclass
class InteractionCallbackDataAutocomplete:
    choices: List[ApplicationCommandOptionChoice]

@dataclass
class InteractionCallbackDataModal:
    custom_id: str # string	a developer-defined identifier for the component, max 100 characters
    title: str # string	the title of the popup modal, max 45 characters
    components: List[Component] # array of components	between 1 and 5 (inclusive) components that make up the modal

InteractionCallbackData =  Union[InteractionCallbackDataMessages, InteractionCallbackDataAutocomplete, InteractionCallbackDataModal]

@dataclass
class InteractionResponse:
    type: InteractionCallbackType
    data: Optional[InteractionCallbackData] = None

# This is what is sent back to us when we create a command
@dataclass
class ApplicationCommand:
    id: Snowflake # snowflake	Unique ID of command	all
    application_id: Snowflake # snowflake	ID of the parent application	all
    name: str # string	Name of command, 1-32 characters	all
    description: str # string	Description for CHAT_INPUT commands, 1-100 characters. Empty string for USER and MESSAGE commands	all
    version: Snowflake # snowflake	Autoincrementing version identifier updated during substantial record changes	all
    type: CommandType = CommandType.CHAT # one of application command type	Type of command, defaults to 1	all
    guild_id: Optional[Snowflake] = None # snowflake	guild id of the command, if not global	all
    name_localizations: Optional[dict] = None # dictionary with keys in available locales	Localization dictionary for name field. Values follow the same restrictions as name	all
    description_localizations: Optional[dict] = None # dictionary with keys in available locales	Localization dictionary for description field. Values follow the same restrictions as description	all
    options: Optional[List[ApplicationCommandOption]] = None # array of application command option	Parameters for the command, max of 25	CHAT_INPUT
    default_member_permissions: Optional[str] = None # string	Set of permissions represented as a bit set	all
    dm_permission: Optional[bool] = None # boolean	Indicates whether the command is available in DMs with the app, only for globally-scoped commands. By default, commands are visible.	all
    default_permission: Optional[bool] = None # boolean	Not recommended for use as field will soon be deprecated. Indicates whether the command is enabled by default when the app is added to a guild, defaults to true	all

import abc
import logging


class AlexaBaseHandler(object):
    """
    Base class for a python Alexa Skill Set
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def my_logger(self, event, context):
        self.logger.info('Event:{}'.format(event))
        self.logger.info('Context:{}'.format(context))
        # self.logger.error('')
        return

    @abc.abstractmethod
    def on_launch(self, launch_request, session):
        """
        Called when the user launches the skill without specifying what
        they want. eg. when the user issues a:

        Alexa, open <invocation name>
        :param launch_request:
        :param session:
        :return: output of _build_response
        """
        pass

    @abc.abstractmethod
    def on_session_started(self, session_started_request, session):
        """
        Called when the session starts """
        pass

    @abc.abstractmethod
    def on_intent(self, intent_request, session):
        """
        Called when the user specifies an intent for this skill

        :param intent_request:
        :param session:
        :return: output of _build_response
        """
        pass

    @abc.abstractmethod
    def on_session_ended(self, session_ended_request, session):
        """
        Called when the user ends the session.
        Is not called when the skill returns should_end_session=true

        :param session_ended_request:
        :param session:
        :return: output of _build_response
        """
        pass

    @abc.abstractmethod
    def on_processing_error(self, event, context, exc):
        """
        If an unexpected error occurs during the process_request method
        this handler will be invoked to give the concrete handler
        an opportunity to respond gracefully

        :param exc exception instance
        :return: output of _build_response
        """
        pass

    def process_request(self, event, context):
        """
        Helper method to process the input Alexa request and
        dispatch to the appropriate on_ handler

        :param event:
        :param context:
        :return: response from the on_ handler
        """

        # if its a new session, run the new session code
        try:
            response = None
            if event['session']['new']:
                self.on_session_started({'requestId': event['request']['requestId']}, event['session'])

            # regardless of whether its new, handle the request type
            if event['request']['type'] == "LaunchRequest":
                response = self.on_launch(event['request'], event['session'])
            elif event['request']['type'] == "IntentRequest":
                response = self.on_intent(event['request'], event['session'])
            elif event['request']['type'] == "SessionEndedRequest":
                response = self.on_session_ended(event['request'], event['session'])

        except Exception as exc:
            response = self.on_processing_error(event, context, exc)

        return response

    # --------------- Helpers that build all of the responses -----------------
    def _build_speechlet_response_without_card(self, speech_output, reprompt_text, should_end_session):
        """
        Internal helper method to build the speechlet portion of the response without the card
        """
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': speech_output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }

    def _build_speechlet_response(self, card_title, card_output, speech_output, reprompt_text, should_end_session):
        """
        Internal helper method to build the speechlet portion of the response
        """
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': speech_output
            },
            'card': {
                'type': 'Simple',
                'title': card_title,
                'content': card_output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }

    def _build_speechlet_ssml(self, card_title, card_output, speech_output, reprompt_text, should_end_session):
        """
        Internal helper method to build the speechlet portion of the response
        """
        return {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak>' + speech_output + '</speak>'
            },
            'card': {
                'type': 'Simple',
                'title': card_title,
                'content': card_output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }

    def _build_response(self, session_attributes, speechlet_response):
        """
        Internal helper method to build the Alexa response message
        :return: properly formatted Alexa response
        """
        return {
            'version': '1.0',
            'sessionAttributes': session_attributes,
            'response': speechlet_response
        }

    def _build_quick_response(self, intent_request, session, msg):
        speech_output = msg  # str
        reprompt_text = None
        should_end_session = False

        speechlet = self._build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)

        return self._build_response(session['attributes'], speechlet)

    def _is_intent(self, intent_name, intent_request):
        return self._get_intent_name(intent_request) == intent_name

    def _get_intent(self, intent_request):
        if 'intent' in intent_request:
            return intent_request['intent']
        else:
            return None

    def _get_intent_name(self, intent_request):
        intent = self._get_intent(intent_request)
        intent_name = None
        if intent is not None and 'name' in intent:
            intent_name = intent['name']

        return intent_name

    def _slot_exists(self, slot_name, intent_request):
        intent = self._get_intent(intent_request)
        if intent is not None:
            return slot_name in intent['slots']
        else:
            return False

    def _get_slot_value(self, slot_name, intent_request):
        value = None
        try:
            if self._slot_exists(slot_name, intent_request):
                intent = self._get_intent(intent_request)
                value = intent['slots'][slot_name]['value']
            else:
                value = None
        except Exception as exc:
            self.logger.exception("Error getting slot value for slot_name={0}"
                                  .format(slot_name))

        return value

    def _attribute_exists(self, attribute_name, session):
        """
        :param attribute_name: str
        :param session: dict
        :return: bool
        """
        if attribute_name in session['attributes']:
            return True
        else:
            return False

    def _get_attribute(self, attribute_name, session):
        attribute = None
        try:
            if self._attribute_exists(attribute_name, session):
                attribute = session['attributes'][attribute_name]
            else:
                attribute = None
        except Exception as exc:
            self.logger.exception("Error getting attribute for attribute={0}"
                                  .format(attribute_name))

        return attribute

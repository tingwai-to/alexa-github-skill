from AlexaBaseHandler import AlexaBaseHandler
import github


class AlexaDeploymentHandler(AlexaBaseHandler):
    def __init__(self):
        super(self.__class__, self).__init__()

    def on_processing_error(self, event, context, exc):
        print(event, context, exc)
        print("on processing error")

    def on_session_started(self, session_started_request, session):
        print("on_session_started requestId=" + session_started_request['requestId']
              + ", sessionId=" + session['sessionId'])

    def on_launch(self, launch_request, session):
        print("on_launch requestId=" + launch_request['requestId'] +
              ", sessionId=" + session['sessionId'])

        return self.get_welcome_response()

    def on_session_ended(self, session_ended_request, session):
        print("on_session_ended requestId=" + session_ended_request['requestId'] +
              ", sessionId=" + session['sessionId'])

        session_attributes = {}
        speech_output = "Exiting Alexa github skill from on session ended."
        reprompt_text = None
        should_end_session = True

        speechlet = self._build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def on_intent(self, intent_request, session):
        print("on_intent requestId=" + intent_request['requestId']
              + ", sessionId=" + session['sessionId'])

        intent = intent_request['intent']
        intent_name = intent_request['intent']['name']

        # Dispatch to skill's intent handlers
        if intent_name == "TopRepos":
            return self.handle_top_repo(intent, session)
        elif intent_name == "AMAZON.HelpIntent":
            return self.get_welcome_response()
        elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
            return self.handle_session_end_request()
        else:
            raise ValueError("Invalid intent")

    def get_welcome_response(self):
        """
        Handle skill on_launch. Will repeat if user does not reply
        :return: output of _build_response
        """
        session_attributes = {}
        card_title = "Welcome"
        card_output = "Welcome to Github top repositories. " \
                      "Try asking me, " \
                      "what are the top repositories on github?"
        speech_output = card_output
        reprompt_text = "I didn't catch that. " \
                        "Try asking me, " \
                        "what are the top repositories on github?"
        should_end_session = False

        speechlet = self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def handle_session_end_request(self):
        session_attributes = {}
        speech_output = "Exiting Alexa github skill from handle session end request."
        reprompt_text = None
        should_end_session = True

        speechlet = self._build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def handle_top_repo(self, intent, session):
        repos = github.get_top_repo()

        speech_readout = "Top five repos this week are,\n "
        for i, repo in enumerate(repos):
            speech_readout += "#{0}. Name: {1}. Description: {2}. Language: {3}. "\
                .format(i+1, repo['name'], repo['description'], repo['language'])

        card_readout = "Top five repos this week are, "
        for i, repo in enumerate(repos):
            card_readout += "#{0}. {1}\n "\
                            "Description: {2}\n "\
                            "Language: {3}\n "\
                            "URL:{4}\n "\
                .format(i+1, repo['name'], repo['description'],
                        repo['language'], repo['html_url'])

        session_attributes = {}
        card_title = "Top 5 GitHub Repos"
        card_output = card_readout
        speech_output = speech_readout
        reprompt_text = None
        should_end_session = False

        speechlet = self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

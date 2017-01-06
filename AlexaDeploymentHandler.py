from __future__ import print_function
from AlexaBaseHandler import AlexaBaseHandler
import github
import random


class AlexaDeploymentHandler(AlexaBaseHandler):
    def __init__(self):
        super(self.__class__, self).__init__()

    def on_processing_error(self, event, context, exc):
        print("on_processing_error", event, context, exc)

    def on_session_started(self, session_started_request, session):
        print("on_session_started")

    def on_launch(self, launch_request, session):
        print("on_launch")

        return self.get_welcome_response()

    def on_session_ended(self, session_ended_request, session):
        session_attributes = {}
        speech_output = "Exiting Repo Tree."
        reprompt_text = None
        should_end_session = True

        speechlet = self._build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def on_intent(self, intent_request, session):
        """
        Handles "IntentRequest".

        Args:
            intent_request (dict): from Alexa
            session (dict): from Alexa

        Returns:
            (func): handle functions corresponding to intent

        Raises:
            ValueError: when intent is not supported
        """
        intent_name = intent_request['intent']['name']
        print(intent_name)

        # Dispatch to skill's intent handlers
        if intent_name == "TopRepos":
            return self.handle_top_repo(intent_request, session)
        elif intent_name == "RepeatRepo":
            return self.handle_repeat_repo(intent_request, session)
        elif intent_name == "FeelingLucky":
            return self.handle_feeling_lucky(intent_request, session)
        elif intent_name == "AMAZON.HelpIntent":
            return self.handle_help_response()
        elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
            return self.handle_session_end_request()
        else:
            raise ValueError("Invalid intent")

    def get_welcome_response(self):
        """
        Welcome response. Repeats speech if user does not reply.

        Returns:
            _build_response: passed to Alexa
        """
        session_attributes = {}
        card_title = "Welcome"
        card_output = "Welcome to Repo Tree. " \
                      "Try asking me about the top repositories on GitHub."
        speech_output = card_output
        reprompt_text = "I didn't catch that. " \
                        "Try asking me about the top repositories on GitHub."
        should_end_session = False

        speechlet = self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def handle_help_response(self):
        """
        intent: "AMAZON.HelpIntent"
        Provides help and examples.

        Returns:
            _build_response: passed to Alexa
        """
        session_attributes = {}
        card_title = "Help"
        card_output = \
            "Repo Tree tracks the top trending repositories on GitHub. " \
            "I can also filter them by the past day, week, month, or year in most programming languages. " \
            "For example, try asking me, what're the top repos in the past week written in Python. \n" \
            "More examples: \n" \
            "Alexa, ask Repo Tree about the top repos \n" \
            "Alexa, ask Repo Tree what're the top Python repos \n" \
            "Alexa, ask Repo Tree what're top repos in the past month \n" \
            "Alexa, ask Repo Tree about the top repos in the past week written in Java \n"
        speech_output = \
            'Repo Tree <break time="0.1s"/> tracks the top trending repositories on GitHub. ' \
            'I can also filter them by the past day, <break time="0.1s"/> week, <break time="0.1s"/> month, or year <break time="0.1s"/> in most programming languages. ' \
            'For example, try asking me, what\'re the top repos in the past week written in Python.'
        reprompt_text = "Check your Alexa app for more examples."
        should_end_session = False

        speechlet = self._build_speechlet_ssml(card_title, card_output, speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def handle_session_end_request(self):
        """
        intent: "AMAZON.CancelIntent" or "AMAZON.StopIntent"
        Ends session.

        Returns:
             _build_response: passed to Alexa
        """
        session_attributes = {}
        speech_output = "Exiting Repo Tree."
        reprompt_text = None
        should_end_session = True

        speechlet = self._build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def handle_top_repo(self, intent_request, session):
        """
        intent: "TopRepos"
        Gets (optional) slot value of {Date} and {Language} then builds response.

        Args:
            intent_request (dict): from Alexa
            session (dict): from Alexa

        Returns:
            create_repo_response: speechlet response
        """
        print(intent_request)

        date = self._get_slot_value('Date', intent_request)
        language = self._get_slot_value('Language', intent_request)
        print(date, language)

        return self.create_repo_response(date, language)

    def handle_repeat_repo(self, intent_request, session):
        """
        intent: "RepeatRepo"
        Handles when user asks to repeat a repo previously retrieved/read.

        Note:
            Calls welcome response if user attempts to repeat a repo
            without invoking the "TopRepos" intent during session.
            Tells user an error if user attempts to repeat a repo outside
            of range.

        Args:
            intent_request (dict): from Alexa
            session (dict): from Alexa

        Returns:
            _build_response: passed to Alexa
        """
        repeat_num = self._get_slot_value('Number', intent_request)  # str
        repeat_num = str(int(repeat_num)-1)  # account for 0 index, #1->index_0

        top_repos = self._get_attribute('top_repos', session)
        # None if user asks to repeat a number without asking for repos first
        if top_repos is None:
            return self.get_welcome_response()

        # when user asks for a number not provided earlier
        if repeat_num not in top_repos:
            speechlet = self._build_speechlet_response_without_card(
                "#{0} not available".format(int(repeat_num) + 1),
                "Try asking me something else.", False)

            return self._build_response(session['attributes'], speechlet)

        repo = top_repos[repeat_num]
        speech_output = "#{0}. Name: {1}. Description: {2}. Language: {3}. " \
            .format(int(repeat_num)+1, repo['name'],
                    repo['description'], repo['language'])
        speech_output += "If you would like to hear something again, " \
                         "ask me to repeat a number."

        reprompt_text = "More repo details can be found in your Alexa app."
        should_end_session = False

        speechlet = self._build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)

        return self._build_response(session['attributes'], speechlet)

    def handle_feeling_lucky(self, intent_request, session):
        """
        intent: "FeelingLucky"
        Randomizes a date and language.

        Note:
            LIST_OF_TIME and LIST_OF_PROGRAMMING_LANGUAGES files are located
            in a subdirectory but is copied to root when a .zip is created
            from create_deployment.py

        Args:
            intent_request (dict): from Alexa
            session (dict): from Alexa

        Returns:
            create_repo_response: speechlet response
        """
        with open('LIST_OF_TIME') as date_file:
            all_date = [line.strip() for line in date_file.readlines()]
        with open('LIST_OF_PROGRAMMING_LANGUAGES') as language_file:
            all_languages = [line.strip() for line in language_file.readlines()]

        rand_date = random.choice(all_date)
        rand_language = random.choice(all_languages)
        print(rand_date, rand_language)

        return self.create_repo_response(rand_date, rand_language)

    def create_repo_response(self, date, language):
        """
        Performs GitHub search API call using date and language arguments.
        Creates speechlet response for Alexa including card/speech output.

        Note:
            If no date/language is specified, date defaults to past day and
            language defaults to all programming languages in GitHub

        Args:
            date (str): the past [day, week, month, year]
            language (str): programming languages, see LIST_OF_PROGRAMMING_LANGUAGES

        Returns:
            _build_response: passed to Alexa
        """
        top_repos = github.get_top_repo(date_value=date, language_value=language)
        N_REPOS = len(top_repos)

        if date is None and language is None:
            date_readout = 'day'
            language_readout = ''
        elif date is None and language is not None:
            date_readout = 'day'
            language_readout = github.convert_language(language)
        elif date is not None and language is None:
            date_readout = date
            language_readout = ''
        else:
            date_readout = date
            language_readout = github.convert_language(language)

        speech_readout = "Top {0} {2} repos in the past {1} are, \n"\
            .format(N_REPOS, date_readout, language_readout)
        card_readout = "Top {0} {2} repos in the past {1}: \n"\
            .format(N_REPOS, date_readout, language_readout)

        for i in range(N_REPOS):
            repo = top_repos[str(i)]

            speech_readout += "#{0}. Name: {1}. Description: {2}. Language: {3}. " \
                .format(i+1, repo['name'], repo['description'], repo['language'])

            card_readout += "#{0}. {1} \n" \
                            "Description: {2} \n" \
                            "Language: {3} \n" \
                            "URL: {4} \n" \
                .format(i+1, repo['name'], repo['description'],
                        repo['language'], repo['html_url'])
        speech_readout += "If you would like to hear a repo again, " \
                          "ask me to repeat a number."

        session_attributes = {'top_repos': top_repos}
        card_title = "Top {0} GitHub Repos".format(N_REPOS)
        card_output = card_readout
        speech_output = speech_readout
        reprompt_text = "More repo details can be found in your Alexa app."
        should_end_session = False

        speechlet = self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

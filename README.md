#Alexa GitHub Skill

With alexa-github-skill, called Repo Tree for now, you can interface with an Amazon Echo/Alexa to track the top trending repositories on GitHub. Repos can be filtered by time frame (past day/week/month/year) and programming language.

Examples:
```
Alexa, ask Repo Tree the top repos
Alexa, ask Repo Tree what're the top Python repos
Alexa, ask Repo Tree what are top repos in the past month
Alexa, ask Repo Tree the top repos in the past week written in Java
```

When a time frame is not specified, top repos from the past day are returned. When a language is not specified, top repos from all languages are returned.

#Voice Design

Intent tree:
```
Welcome
├───TopRepos
│   │   {Date}
│   │   {Language}
│   │
│   └───RepeatRepo
│           {Number}
│
├───FeelingLucky
│   │   {Date}      // random
│   │   {Language}  // random
│   │
│   └───RepeatRepo
│           {Number}
│
├───Help
│
└───Stop/Cancel
```
{Text} indicates slots associated with the skill. Welcome screen can be skipped if intents are directly invoked through Alexa.

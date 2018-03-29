# REST API

## POST /annotate/`operation`?lang=`language`
This analysis produces a list of annotations for a given text. That text has to be provided in the POST's request body.

### Parameters

#### `operation` (required)
The wanted operation.

Possible values:
- `NER`, named entity recognition
- `POS`, part of speed tagging
- `all`, all the above 

#### `language` (optional)
Specify the text's language instead of letting the NLP components try to decide automatically.

Possible values:
- `de`, German
- `en`, English
- `it`, Italian
- `fr`, French

### Return values

#### 202 Accepted

Returns a JSON containing the task ID (see below).

Example:
```
{
    "status": "Accepted",
    "task": "79153af8-634d-42e4-80f2-bd430262e54c"
}
```

#### 4xx

Todo


## POST /get-entities/`entity_type`?lang=`language`

This analysis searches and returns named entities in a text. That text has to be provided in the POST request body.

### Parameters
#### `entity_type` (optional)
Specify the kind of entity you want to extracted. Defaults to all types.

Possible values:
- `locations`
- `persons`
- `organisations`

#### `language` (optional)
Specify the text's language instead of letting the NLP components try to decide automatically.

Possible values:
- `de`, German
- `en`, English
- `it`, Italian
- `fr`, French

### Return values

#### 202 Accepted

Returns a JSON containing the task ID (see below).

Example:
```
{
    "status": "Accepted",
    "task": "79153af8-634d-42e4-80f2-bd430262e54c"
}
```

#### 4xx

Todo


## GET /status/`task_id`

Get the status for the task, specified by the task ID.

### Parameters

#### `task_id` (required)
The task's ID, as returned by one of the POST requests described above.

### Return values

#### 200 Ok

JSON response for the requested analysis.

Example for a running task:

```
{
    "state": "PROGRESS",
    "status": "Running NLP analysis..."
}
```


Example for a finished task: 

```
{
    "result": {
        "detected_language": "de",
        "named_entities": [
            [
                "Der",
                "O"
            ],
            [
                "Parthenon",
                "O"
            ],
            [
                "(",
                "O"
            ],
            [
                "griechisch",
                "O"
            ],
            [
                "παρθενών",
                "O"
            ],
            [
                "„",
                "O"
            ],
            [
                "Jungfrauengemach",
                "O"
            ],
            [
                "“)",
                "O"
            ],
            [
                "ist",
                "O"
            ],
            [
                "der",
                "O"
            ],
            [
                "Tempel",
                "O"
            ],
            [
                "für",
                "O"
            ],
            [
                "die",
                "O"
            ],
            [
                "Stadtgöttin",
                "O"
            ],
            [
                "Pallas",
                "I-ORG"
            ],
            [
                "Athena",
                "I-ORG"
            ],
            [
                "Parthenos",
                "O"
            ],
            [
                "auf",
                "O"
            ],
            [
                "der",
                "O"
            ],
            [
                "Athener",
                "I-LOC"
            ],
            [
                "Akropolis",
                "I-LOC"
            ],
            [
                ".",
                "O"
            ],
            (...)
        ],
        "sentence_count": 271,
        "word_count": 5968
    },
    "state": "SUCCESS",
    "status": "Processing completed."
}
```

TODO: Give examples for results in POST request descriptions above. Focus on task status here.

#### 4xxx

TODO

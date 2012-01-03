<hr />
**API Documentation**

The below documentation will use http://127.0.0.1:8085/ as the base URL for Gamez and the api_key of "ikzFRzA1Y8I1UajNJAOQ803TbTYk1vLB64A9SxrAxAw"
<hr />
*General*

The API function for Gamez is accessed through the '/api' page (http://localhost:8085/api)

JSON responses will be returned.

If the URL is accessed without any parameters, an error will be returned in the format: [{"Error" : "Error Message"}]

The API Key is a required parameter

Currently, no API actions are implemented.

<hr />
*Parameters*

API_KEY - The Gamez API Key (Can be retrieved from Settings page)
MODE - The type of request. Valid values: ["search"]
TERM - Used with search and should be part of the game name
SYSTEM - The name of the system corresponding with the action

<hr />
*Modes*

***SEARCH***
<br />
This mode searches for a game. A json response will be returned containing all games matching the search term. The term parameter should be supplied. If it is blank or not supplied, all games will be returned

Examples:
Get list of all games: http://127.0.0.1:8085/api?api_key=ikzFRzA1Y8I1UajNJAOQ803TbTYk1vLB64A9SxrAxAw&mode=search
Search for games that contain "Super" and are only for the Wii: http://127.0.0.1:8085/api?api_key=ikzFRzA1Y8I1UajNJAOQ803TbTYk1vLB64A9SxrAxAw&mode=search&term=super&system=wii

</hr>
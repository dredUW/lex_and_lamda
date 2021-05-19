###Unit-13 Python Script###
### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

def validate_data(age, investment_amount, intent_request):
    """
    Validates the data provided by the user
    """
    
    #Validate that the user is at least 18 years old, but less than 65 years old
    if age is not None:
        #Parameters are strings and need to be cast as values
        age = parse_int(age)
        if age < 18:
            return build_validation_result(
                False,
                "age",
                "You must be at least 18 years old to use this service, "
                "please come back when you are older.",)
        elif age >= 65:
            return build_validation_result(
                False,
                "age",
                "You must be under 65 years old to use this service,"
                "for help with retirement please call our toll free number,"
                "at 800-800-8000 to speak with a specialist.",)
                
    #Validate investment amount is at least 5000
    if investment_amount is not None:
        investment_amount = parse_int(investment_amount)
        if investment_amount < 5000:
            return build_validation_result(
                False,
                "investmentAmount",
                "You must invest a minimum of $5,000 to use this service, "
                "please adjust your investment amount.",)
                
    #If age and investment_amount evaluate to true then data is valid
    return build_validation_result(True, None, None)

def get_recommendation(risk_level, intent_request):
    if risk_level == "None":
        port_rec = "100% bonds (AGG) and 0% equities (SPY)"
    elif risk_level == "Very Low":
        port_rec = "80% bonds (AGG) and 20% equities (SPY)"
    elif risk_level == "Low":
        port_rec = "60% bonds (AGG) and 40% equities (SPY)"
    elif risk_level == "Medium":
        port_rec = "40% bonds (AGG) and 60% equities (SPY)"
    elif risk_level == "High":
        port_rec = "20% bonds (AGG) and 80% equities (SPY)"
    elif risk_level == "Very High":
        port_rec = "0% bonds (AGG) and 100% equities (SPY)"
    return port_rec

### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.
        
        ### YOUR DATA VALIDATION CODE STARTS HERE ###
        
        #Get all the slots
        slots = get_slots(intent_request)
        
        #Call validation function to validate user inputs
        validation_result = validate_data(age, investment_amount, intent_request)
        
        #if the data is not valid, the elicitslot dialog action is called to
        #re-prompt for the first violation detected
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None #Cleanse the invalid slot
            
            #Return elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
                )
        
        ### YOUR DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
    initial_recommendation = get_recommendation(risk_level, intent_request)
    

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

     #Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)

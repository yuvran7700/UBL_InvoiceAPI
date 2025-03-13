import boto3

dynamodb = boto3.resource("dynamodb")

def delete_all_user_items():
    """Deletes all items from a DynamoDB table."""
    table_name = "users"
    table = dynamodb.Table(table_name)
    response = table.scan()  # Get all items
    items = response.get("Items", [])

    while "LastEvaluatedKey" in response:  # Continue if there are more items
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    # Batch delete (DynamoDB limits batch writes to 25 items per request)
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"email": item["email"]})  


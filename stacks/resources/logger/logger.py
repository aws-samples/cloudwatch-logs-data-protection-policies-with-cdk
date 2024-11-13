import json
import logging
import random
import string
from typing import Any

# set logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    
    # print the event details
    logger.debug(json.dumps(event, indent=2))

    user_id = generate_random_data(string.ascii_lowercase, 8)
    
    employee_id = generate_random_data(string.digits, length=9)

    # writing log information
    logger.info(f"Processing data for user id: {user_id}")

    # ip address - to be masked
    logger.info(f"User connecting from ip address: {generate_random_ip_address()}")

    # email address - to be masked
    logger.info(f"Email address for {user_id}: {user_id}@fakedomain.com")

    # aws secret key - to be masked
    logger.info(f"User id: {user_id} has employee id: EmployeeId-{employee_id}")


def generate_random_data(string_type: Any, length: int) -> str:

    return ''.join(
        random.choices(
            string_type,
            k=length
        )
    )

def generate_random_ip_address() -> str:

    return ".".join(str(random.randint(0, 255)) for _ in range(4))

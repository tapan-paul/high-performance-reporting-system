import csv
import random

def generate_10k_test(filename="large_data.csv"):
    """
    generate a large input to test the async non-blocking 
    whilst this is happening calling POST /execute endpoint, call the GET /reporting/{format} and this should be responsive
    
    :param filename: Description
    """
    currencies = ['USD', 'EUR', 'GBP', 'AUD', 'JPY', 'CAD'] # JPY/CAD will fail
    channels = ['CHANNEL1', 'CHANNEL2', 'CHANNEL3', 'CHANNEL4']
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['external_id', 'amount', 'currency', 'source_channel'])
        for i in range(10000):
            # Purposefully create a few bad records (negative amount or unsupported currency)
            is_valid = random.random() > 0.1 # 10% will be "bad"
            writer.writerow([
                f"TXN-{10000+i}",
                round(random.uniform(10.0, 5000.0), 2) if is_valid else -50.0,
                random.choice(currencies),
                random.choice(channels)
            ])
    print(f"✅ Generated {filename} with 10,000 rows.")

generate_10k_test()

"""Send an email when the rain probability for that day is greater than a 
given value.

This script is thought to be executed daily at 8:00am. As such, the code 
checks for the first two values of the rain probability inside the given url. 
In the case of the chosen weather website, these will always be the rain 
probability for the morning and afternoon of that same day.

If the probability is greater than a chosen value, an email will be sent with
a message to pick up an umbrella.

Script based on the one from this exercise
https://www.geeksforgeeks.org/schedule-a-python-script-to-run-daily/
with many modifications to adapt for this use case.
"""

import re
import requests
import smtplib

url = "https://www.aemet.es/en/eltiempo/prediccion/municipios/barcelona-id08019"
html = requests.get(url).content    

def extract_rain_probabilities(html_bytes):
  """Get the first two values of 'rainfaill probability' from aemet's web."""
    
  # Try decoding with 'latin-1' first, fallback to 'utf-8' if it fails
  try:
    html_string = html_bytes.decode('latin-1')
  except UnicodeDecodeError:
    html_string = html_bytes.decode('utf-8', errors='ignore')  # Ignore decoding errors for 'utf-8'

  # In the given url, rainfall probabilities appear after second occurrence of "Rainfall probability"
  first_occurrence = html_string.find("Rainfall probability")
  if first_occurrence == -1:
    return None, None

  second_occurrence = html_string.find("Rainfall probability", first_occurrence + 1)
  if second_occurrence == -1:
    return None, None

  # Start looking after the second occurrence
  start_index = second_occurrence + len("Rainfall probability")
  substring = html_string[start_index:]

  # Find the first rain probability with regex
  first_percentage_match = re.search(r'>(\d+)%', substring)
  if first_percentage_match:
    first_percentage = first_percentage_match.group(1) + "%"
  else:
    first_percentage = None

  # Find the second rain probability with regex
  second_substring = (substring.split(first_percentage, 1)[1] 
                      if first_percentage else substring)
  second_percentage_match = re.search(r'>(\d+)%', second_substring)
  if second_percentage_match:
      second_percentage = second_percentage_match.group(1) + "%"
  else:
      second_percentage = None

  rain_prob1 = int(first_percentage[:-1]) / 100
  rain_prob2 = int(second_percentage[:-1]) / 100
  
  return rain_prob1, rain_prob2

# Apply function
rain_prob1, rain_prob2 = extract_rain_probabilities(html)

rain_prob1_str = f"{str(rain_prob1*100)}%"
rain_prob2_str = f"{str(rain_prob2*100)}%"

# Display probabilities
if rain_prob1 and rain_prob2:
    print(f"Morning rain probability: {rain_prob1_str}")
    print(f"Afternoon rain probability: {rain_prob1_str}")
else:
    print("Rain probabilities not found.")
    
# Create smtp object if probabilities are higher than a given value
rain_prob_threshold = 0.3
if rain_prob1 > rain_prob_threshold or rain_prob2 > rain_prob_threshold :
	smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
else: print("no rain today")

# Start TLS for security
smtp_object.starttls()

# Authentication
smtp_object.login("EMAIL", "PASSWORD")
subject = "Que hoy llueve chaval!"
body = ("Coge paraguas.\n"
        f"La probabilidad de lluvia para esta mañana es de {rain_prob1_str}.\n"
        f"La probabilidad de lluvia para esta tarde es de {rain_prob2_str}.")

msg = (f"Subject:{subject}\n\n{body}\n\nSaludos,\nLas nubes.").encode('utf-8')

# Sending the mail
smtp_object.sendmail("EMAIL TO SEND FROM", "EMAIL TO SEND TO", msg)

# Terminating the session
smtp_object.quit()
print("Email Sent!")
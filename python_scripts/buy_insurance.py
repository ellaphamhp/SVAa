import requests

quote = requests.get("https://subscribe.axa-schengen.com/en/step1?langue=en&product=16&number_people=1&date_format=d/m/Y&start_date=14/10/2022&end_date=17/10/2022&op=GET%20A%20QUOTE&form_build_id=form-xCUuij68b_AduwilLs4n4DkCfX1gSHz4R7yumrSLbNE&form_id=subscription_quote_form&cagree=2")
print(quote.text)
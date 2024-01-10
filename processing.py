import pandas as pd
import re

def process(data):
    # note in streamlit we taking data using utf-8 so these symbols are not present there..(a space is there) so it is not required
    # data = data.replace("â€¯", " ")

    pattern = "\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{1,2}\s..\s-\s"

    d1 = re.split(pattern, data)[1:]  # to remove empty '' we remove first item from list
    d1 = [x[:-1] for x in d1]

    d2 = re.findall(pattern, data)
    d2 = [x.replace(" - ", "") for x in d2]

    df = pd.DataFrame({"Date": d2, "Messages": d1})

    users = []
    msg = []

    # there can be many : so how to do..we can use re..for smart see the video..here is my way
    # re.search return first occurence return match object , so use findall return list of matchings

    # we are just searching :\s may be in a text these can be found ..but htis not problem
    # as these large messages with such a pattern not send by whatsapp so it will definitely users message
    # so we will split at first occurence if found
    # read about re module : https://pynative.com/python-regex-split/

    for message in df["Messages"]:
        pattern = ":\s"
        found = re.findall(pattern, message)

        # if :\s present means definitely it will be user msg..but can be multiple :\s so break at first occurence..as wP not send this type of messages
        if found:
            parts = re.split(pattern, message, maxsplit=1)
            users.append(parts[0])  # can be multiple matches so takes oth index that will be user
            msg.append(parts[1])

        # users not present means group notification
        # means it is definitely whatsapp msg as WP never send :\s pattern
        else:
            users.append("Group_Notification")
            msg.append(message)

    # update the dataframeor add new columns also
    df["Users"] = users
    df["Messages"] = msg

    df2 = df.copy()

    df2["Date"] = pd.to_datetime(df2["Date"], dayfirst = True)  

    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                   'November', 'December']


    df2["Day"] = df2["Date"].apply(lambda x: x.day)

    df2["Month"] = df2["Date"].apply(lambda x: month_names[x.month - 1])  # using list make above

    df2["Year"] = df2["Date"].dt.year

    df2["Hour"] = df2["Date"].apply(lambda x: x.hour)

    df2["Minute"] = df2["Date"].dt.minute


    return df2

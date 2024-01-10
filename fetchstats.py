import re
from collections import Counter
import pandas as pd
import emoji
from urlextract import URLExtract

def final_string_wordslist_userbased(select,df2):

    if select != "OverAll":
        df2 = df2[df2["Users"] == select]

    string = ""
    up_df2 = df2[df2["Messages"] != "<Media omitted>"]
    up_df2 = up_df2[up_df2["Users"] != "Group_Notification"]
    for i in up_df2["Messages"]:
        string = string + " " + i

    string = string.lower()
    # string has a space in begining remove it
    string = string[1:]

    possiblechars = r"""!@#$%^&/*(){[]}-'"+/.,:;?\'>\"<"""

    wordslist = re.split(",|\s|\n|\?|\.",string)

    wordslist = [x for x in wordslist if x != ""]

    wordslist = [x for x in wordslist if x not in possiblechars]

    wordslist = [x.strip(possiblechars) for x in wordslist]

    wordslist = [x for x in wordslist if x != ""]

    finalstring = (" ").join(wordslist)

    return finalstring, wordslist

def fetch_stats(selected, df, finalstring, wordslist):
    if selected != "OverAll":
        df = df[df["Users"] == selected]

    # note this also include group notification messages also...so remove them dont exclude medais these are msges
    totalmsg = df[df["Users"] != "Group_Notification"].shape[0]

    # count words - not having media and notification
    totalwords = len(wordslist)

    # count medias
    totalmedia = df[df["Messages"] == "<Media omitted>"].shape[0]

    # count total links

    extractor = URLExtract()
    links = []
    for i in df["Messages"]:
        links.extend(extractor.find_urls(i))

    totallinks = len(links)

    return totalmsg, totalwords, totalmedia, totallinks


def most_words(select, df,wordslist, stoplist):
    if select != "OverAll":
        df = df[df["Users"] == select]

    # remove useless words from wordslist
    wrds = [x for x in wordslist if x not in stoplist]

    c = Counter(wrds)

    dc = pd.DataFrame({"Words": c.keys(), "Frequency": c.values()})

    dc = dc.sort_values(by="Frequency", ascending=False).reset_index(drop=True)
    dc = dc.loc[:20, :]

    # just for safety
    return dc[dc["Words"] != ""]

def emojis(select,df):
    if select != "OverAll":
        df = df[df["Users"] == select]

    emojis = []

    for i in df["Messages"]:
        emojis.extend([x for x in i if x in emoji.EMOJI_DATA.keys()])

    c = Counter(
        emojis)  # acts on iterable exactly counts each elements forming the iterable.. in case of string count letters

    df_emoji = pd.DataFrame({"Emoji": c.keys(), "Times Used": c.values()}).sort_values(by="Times Used", ascending=False)
    df_emoji = df_emoji.reset_index(drop=True)

    return df_emoji

def dailytimeline(select, df):

    df = df[df["Users"] != "Group_Notification"]
    if select != "OverAll":
        df = df[df["Users"] == select]

    df["Dateonly"] = df["Date"].dt.date
    dt = df.groupby(["Dateonly"])

    dt = dt["Messages"].count()

    dt = dt.reset_index()

    return dt

def monthlytimeline(select, df):

    df = df[df["Users"] != "Group_Notification"]

    if select != "OverAll":
        df = df[df["Users"] == select]

    d = df.groupby(["Year", "Month"])
    d = d["Messages"].count().reset_index()

    d["Monthly"] = d["Month"] + " " + d["Year"].astype("str")

    return d

def weeklyactivity(select, df):
    df = df[df["Users"] != "Group_Notification"]

    if select != "OverAll":
        df = df[df["Users"] == select]

    df["Weekly"] = df["Date"].dt.day_name()

    w = df.groupby(["Weekly"])["Messages"].count()
    w = w.reset_index()
    w = w.sort_values(by="Messages", ascending=False)

    return w


def monthlyactivity(select, df):
    df = df[df["Users"] != "Group_Notification"]

    if select != "OverAll":
        df = df[df["Users"] == select]

    w = df.groupby(["Month"])["Messages"].count()
    w = w.reset_index()
    w = w.sort_values(by="Messages", ascending=False)

    return w

def hi(x):
    if x == 23:
        return "23-00"
    else:
        return str(x) + '-' + str(x+1)

def heatmap(select, df):
    df = df[df["Users"] != "Group_Notification"]

    if select != "OverAll":
        df = df[df["Users"] == select]

    df["Week"] = df["Date"].dt.day_name()

    df["Week"] = df["Date"].dt.day_name()

    # let sort by hour
    df = df.sort_values(by="Hour")
    df["interval"] = df["Hour"].apply(hi)

    dh = pd.crosstab(df["Week"], df["interval"])

    return dh
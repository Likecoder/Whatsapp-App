import streamlit as st
import processing, fetchstats
from matplotlib import pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import seaborn as sns
import time
from urlextract import URLExtract
from collections import Counter


# https://docs.streamlit.io/library/cheatsheet


st.title(":red[Whatsapp Chat Exploration !]  :green[explore your Chats]")
st.write("It is a tool to analyse the datsets. Here the dataset comprises of whatsapp chats either personally or of groups\n"
         "By importing your WhatsappChatWithSomeone.txt you can see a detailed analysis of your chats\n")

with st.sidebar:    # or simply use st.sidebar.title
    st.title(":blue[Whatsapp Chat Exploration!]")



file = st.sidebar.file_uploader(":red[Please Enter Chat File]", type=["txt"])

if file is not None:

    # we have data in binary formay..we need in string format
    bytes = file.getvalue()
    rawdata = bytes.decode("utf-8")

    # fetch the processed dataframe
    df = processing.process(rawdata)
    st.subheader("Lists of All Messages : ")
    st.write(df)


    stopwords = "bey denge rho ho tum tu kya i u hai"
    stoplist = stopwords.split(" ")
    stoplist.extend(list(STOPWORDS))


    #fetch unique users
    a = list(df["Users"].unique())

    # select box
    a.remove("Group_Notification")
    a.sort(key=lambda x: x.lower())  # first convert all to lower then sort(temporary only for srting without casing of letters)
    a.insert(0,"OverAll")

    # note dont make this select parameter..bcoz as we select other web page got refreshed as select value got changed so only changed select value if button presses
    # so write after button pressed
    selected = st.sidebar.selectbox("Select User",  a)


    # Submit Button
    if st.sidebar.button("Show Analysis"):

        with st.spinner(text='In progress'):
            time.sleep(1)
            bar = st.progress(50)
            time.sleep(1)
            bar.progress(100)
            st.success('Done')
            st.balloons()
            st.snow()




        select = selected

        finalstring_user , wordslist_user = fetchstats.final_string_wordslist_userbased(select, df)

        total_messages, total_words, total_links, total_media = fetchstats.fetch_stats(select,df,finalstring_user, wordslist_user)





        # stats
        st.title("Chats Stats : "+ select)
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown("## :red[Total Messages]")
            st.subheader(f":red[{total_messages}]")
        with c2:
            st.markdown("## :green[Total Words]")
            st.subheader(total_words)
        with c3:
            st.markdown("## :blue[Total Medias]")
            st.subheader(total_media)
        with c4:
            st.markdown("## :orange[Total Links]")
            st.subheader(total_links)


        # show busy users if user then so his mesges list
        if select == "OverAll":

            st.title(":blue[Most Busy Users]")

            c1, c2 = st.columns(2)

            d = df["Users"].value_counts()  # no need to sort already in sort .. it is a series with named indexes of users
            d = d.drop(labels=["Group_Notification"])   #media included

            with c1:
                fig = plt.figure(figsize=(8,8))
                plt.barh(d.head().index, d.head().values, edgecolor="black", color="pink")
                plt.xlabel("Total Messages", fontweight='bold', fontsize=15)
                plt.ylabel("Users", fontweight='bold', fontsize=15)
                plt.title("Most Busy Users", fontweight='bold', fontsize=20, color = "red")
                # plt.xticks(rotation = 270)
                st.pyplot(fig)

            with c2:
                table = d.reset_index()
                table = table.rename(columns = {"Users" : "Top Users","count" : "Total Messages" })

                table["% Chat"] = round( table["Total Messages"] / table["Total Messages"].sum() * 100 , 2)
                table["% Chat"] = table["% Chat"].apply(lambda x: str(x) + "%")
                st.write(table)

        # let show df os user if not Overall in place of Most active users
        else:
            st.title("Chats by : "+select)
            st.write(df[df["Users"] == select])



        # daily timeline

        st.title("Daily Timeline : " + select)

        dt = fetchstats.dailytimeline(select, df)


        fig = plt.figure(figsize=(14, 10))
        plt.plot(dt["Dateonly"], dt["Messages"])
        plt.xlabel("Date", fontsize = 15, fontweight = "bold")
        plt.ylabel("Total Messages", fontsize=15, fontweight="bold")
        plt.title("Daily Timeline", fontsize=20, fontweight="bold", color = "green")
        st.pyplot(fig)


        # monthly timeline
        d = fetchstats.monthlytimeline(select, df)
        st.title("Monthly Timeline : " + select)
        fig = plt.figure(figsize=(14, 10))
        plt.plot(d["Monthly"], d["Messages"])
        plt.xticks(rotation=90)
        plt.xlabel("Month", fontsize=15, fontweight="bold")
        plt.ylabel("Total Messages", fontsize=15, fontweight="bold")
        plt.title("Monthly Timeline", fontweight="bold", fontsize=20, color = "green")
        st.pyplot(fig)


        # weekly activity
        c1, c2 = st.columns(2)

        with c1:
            st.title("Weekly Activity")
            st.subheader(select)
            fig = plt.figure()
            w = fetchstats.weeklyactivity(select, df)
            sns.barplot(data=w, x=w["Weekly"], y=w["Messages"], edgecolor="black", width=0.6, color = "red", saturation=1)
            plt.xlabel("--- Week ---", fontweight="bold", fontsize=15)
            plt.ylabel("Total Messages", fontweight="bold", fontsize=15)
            plt.title("Weekly Activity", fontweight="bold", fontsize=20)
            st.pyplot(fig)



        with c2:
            st.title("Monthly Activity")
            st.subheader(select)
            fig = plt.figure()
            w = fetchstats.monthlyactivity(select, df)
            sns.barplot(data=w, x=w["Month"], y=w["Messages"], edgecolor="black", width=0.6, color = "violet", saturation=1)
            plt.xlabel("--- Month ---", fontweight="bold", fontsize=15)
            plt.ylabel("Total Messages", fontweight="bold", fontsize=15)
            plt.title("Monthly Activity", fontweight="bold", fontsize=20)
            st.pyplot(fig)




        # Showing wordcloud

        # dont simply str,str it is not print().. so add strimg first to show
        st.title("Most Used Words" + " : " + select)

        wordcloud = WordCloud(width=500, height=500, background_color="white", stopwords=set(stoplist))
        wc_img = wordcloud.generate(finalstring_user)

        fig = plt.figure(figsize=(12,7))
        plt.imshow(wc_img)

        plt.axis("off")

        # place the figure on streamlit web page
        st.pyplot(fig)



        # Most Common Used Words

        st.title("Most Common Words : " + select)

        most_used = fetchstats.most_words(select, df, wordslist_user, stoplist)   # as df
        fig = plt.figure()
        plt.barh(most_used["Words"], most_used["Frequency"])
        plt.xlabel("Words" , fontweight=10)
        plt.ylabel("Frequencies", fontweight=10)
        plt.xticks(rotation=90)
        st.pyplot(fig)


        # heatmaps
        st.title("Heat Map : "+select)
        dh = fetchstats.heatmap(select, df)
        fig = plt.figure(figsize=(14, 8))
        sns.heatmap(dh, annot=True)
        plt.xlabel("Hour Interval", fontsize=15, fontweight="bold")
        plt.ylabel("Week", fontsize=15, fontweight="bold")
        plt.title("Activity Map(Messages)", fontsize=20, fontweight="bold")
        st.pyplot(fig)







        # emoji
        st.title("Emoji Analysis : " + select)

        emoji_df = fetchstats.emojis(select,df)

        c1, c2 = st.columns(2)

        with c1:
            st.write(emoji_df)

        with c2:
            s = plt.figure()
            plt.pie(emoji_df["Times Used"], labels=emoji_df["Emoji"], autopct="%.2f%%")
            st.pyplot(s)

with st.sidebar:
    st.markdown("### :red[Steps ----]")
    st.write('''• Go to Whatsapp  >  Open Chats  >  Click Dots > Click More''')
    st.write("• Click on Export Chat  >  select Without Media  >  Save the File ")
    st.write("• Upload File Here ")
    st.write("• Select User  >  Click Show Analysis")
         

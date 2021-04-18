"""Streamlit app that allows users to select their role in the reading group.

To run the app:
```
    streamlit run reading_group_roles.py
```
"""


import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def app_rg():
    # TODO: Read these values from a file
    date = "14th April 2021 18:30 GMT+1"
    paper = "Learning Representations by back-propagating errors"
    paper_link = "https://www.iro.umontreal.ca/~vincentp/ift3395/lectures/backprop_old.pdf"
    dataset_path = "data/reading_group_roles.json"
    participants_path = "data/participants.json"


    st.title("Reading Group by DLSL")
    st.markdown(f"""🗓 **Date:** {date}""")
    st.markdown(
        f"""📝 **Paper:** <a href={paper_link}>{paper}</a>""",
        unsafe_allow_html=True,
    )

    st.set_option('deprecation.showPyplotGlobalUse', False)

    roles = {
        "Mediator": {"max_players": 1, "emoji": "⚖️"},
        "'Good' Peer Reviewer": {"max_players": 4, "emoji": "👼"},
        "'Bad' Peer Reviewer": {"max_players": 4, "emoji": "👿"},
        "Archaeologist": {"max_players": 3, "emoji": "🏺"},
        "Entrepreneur": {"max_players": 3, "emoji": "💼"},
        "Developer": {"max_players": 3, "emoji": "💻"},
        "Journalist": {"max_players": 3, "emoji": "📰"}
    }
    roles_list = list(roles.keys())
    colors = ("#ffadad", "#ffd6a5", "#fdffb6", "#caffbf", "#9bf6ff", "#a0c4ff", "#bdb2ff")

    # Load dataframe
    if os.path.exists(dataset_path):
        df = pd.read_json(dataset_path)
    else:
        df = pd.DataFrame({"Role": roles_list, "Participants": [1] + [0] * (len(roles_list) - 1)})

    # Load participants
    if os.path.exists(participants_path):
        participants_df = pd.read_json(participants_path)
    else:
        participants_df = pd.DataFrame({"name": [], "email": [], "role": []})

    # Side-bar options
    st.sidebar.title("Choose your Role 🧙‍♀️")
    name = st.sidebar.text_input("Name:")
    email = st.sidebar.text_input("Email:")

    option_list = ["--Select--"] + df[df.apply(lambda row: row["Participants"] < roles[row["Role"]]["max_players"], axis=1)]["Role"].tolist()
    chosen_role = st.sidebar.selectbox(
        "Which role would you like to play?",
        option_list
    )

    participant_text = ""

    if chosen_role != "--Select--":
        if not is_email_valid(email):
            participant_text = "⚠️ Please provide a valid email"

        else:
            prev_role = get_role_by_email(participants_df, email)
            if prev_role is not None:
                participant_text = f"⛔️ You have already chosen your role of {prev_role}"
            else:
                # Save participant
                participants_df = participants_df.append(
                    {"name": name, "email": email, "role": chosen_role},
                    ignore_index=True)
                participants_df.to_json(participants_path)

                prep = "an" if chosen_role[0].lower() in ["a", "e", "i", "o", "u"] else "a"
                participant_text = f"You're happy to have you as {prep} {chosen_role} {roles[chosen_role]['emoji']}! " \
                                   f"You can find more info on the event in your mailbox 📬"
                df.loc[df["Role"] == chosen_role, "Participants"] += 1
                # TODO: Send email
                # Save dataframe
                df.to_json(dataset_path)

    # Plot participants
    st.markdown("## Roles")
    plt.barh(df["Role"].tolist(), df["Participants"].tolist(), color=colors)
    plt.gca().invert_yaxis()
    st.pyplot()

    st.markdown(f"**{participant_text}**")


def is_email_valid(text):
    # TODO: Check if email is valid
    return text is not None and len(text) > 0


def get_role_by_email(participants_df, email):
    user_df = participants_df[participants_df["email"] == email]
    if len(user_df) > 0:
        return user_df.iloc[0]["role"]
    else:
        return None


if __name__ == '__main__':
    app_rg()
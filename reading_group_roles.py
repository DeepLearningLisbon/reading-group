"""Streamlit app that allows users to select their role in the reading group.

To run the app:
```
    streamlit run reading_group_roles.py
```
"""

import os
import re
import git
import json
from shutil import copytree, rmtree

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

rules_path = "rules.md"
event_path = "event.json"
roles_path = "roles.json"
storage_path = "data_storage"
data_path = "data"
dataset_path = "data/reading_group_roles.json"
participants_path = "data/participants.json"
branch = 'data'

def app_rg():
    # __________Main Body_____________
    # Make Header with Event Info
    with open(event_path, "r") as f:
        event = json.load(f)
    date = event["date"]
    paper = event["paper"]
    paper_link = event["paper_link"]
    meet_up_link = event["meet_up_link"]

    st.title("Reading Group")
    st.subheader("**by Deep Learning Session Lisbon**")
    st.markdown("")
    st.markdown(f"🗓 **Date:** [{date}]({meet_up_link})")
    st.markdown(f"📝 **Paper:** [{paper}]({paper_link})")
    st.set_option('deprecation.showPyplotGlobalUse', False)

    # Rules
    st.header("Rules")
    with open(rules_path, "r") as f:
        lines = f.read()
        lines = lines.split("\n\n")
        for line in lines:
            st.markdown(line)

    # Explain Roles
    st.header("Roles")
    with open(roles_path, "r") as f:
        roles = json.load(f)
    roles_keys = list(roles.keys())
    col_max = 3
    while len(roles_keys) > 0:
        if len(roles_keys) < col_max:
            col_max = len(roles_keys)
        cols = st.beta_columns(col_max)

        roles_col = roles_keys[:col_max+1]
        roles_keys = roles_keys[col_max:]

        for col, role in zip(cols, roles_col):
            with col:
                st.subheader(f"{role} {roles[role]['emoji']}")
                st.markdown(f"{role}s {roles[role]['description']}")

    # Get Data from github branch
    if "github_token" in st.secrets:
        token = st.secrets["github_token"] + "@"
    else:
        token = ""

    try:
        rmtree(storage_path)
    except:
        pass
    try:
        rmtree(data_path)
    except:
        pass
    repo = git.Repo.clone_from(
        "https://{}github.com/DeepLearningLisbon/reading-group.git".format(token),
        "data_storage")
    current = repo.create_head(branch, repo.remotes.origin.refs[branch])
    current.checkout()
    repo.git.pull('origin', branch)
    copytree(os.path.join(storage_path, data_path), data_path)

    # Load dataframe roles counting
    if os.path.exists(dataset_path):
        df = pd.read_json(dataset_path)
    else:
        roles_list = list(roles.keys())
        participants_list = [roles[role]["taken_by_default"] for role in roles_list]
        df = pd.DataFrame({"Role": roles_list, "Participants": participants_list})
        df[df["Role"]=="Mediator"]["Participants"] = 1

    # Load participants
    if os.path.exists(participants_path):
        participants_df = pd.read_json(participants_path, orient='records')
    else:
        participants_df = pd.DataFrame({"name": [], "email": [], "role": []})


    # __________Sidebar_____________
    st.sidebar.title("Choose your Role 🧙‍♀️")
    name = st.sidebar.text_input("Name:")
    email = st.sidebar.text_input("Email:")

    option_list = ["--Select--"] + df[df.apply(lambda row: row["Participants"] < roles[row["Role"]]["max_players"], axis=1)]["Role"].tolist()
    chosen_role = st.sidebar.selectbox(
        "Which role would you like to play?",
        option_list
    )

    participant_text = ""

    if st.sidebar.button('Submit'):
        valid, participant_text = validate_form(name, email, chosen_role, participants_df)

        if valid:

            # Save participants
            participants_df = participants_df.append(
                {"name": name, "email": email, "role": chosen_role},
                ignore_index=True)
            df.loc[df["Role"] == chosen_role, "Participants"] += 1

            # Store in Json files
            participants_df.to_json(participants_path, orient='records')
            df.to_json(dataset_path)
            for json_path in [participants_path, dataset_path]:
                with open(json_path, "r") as f:
                    j = json.load(f)
                with open(json_path, "w") as f:
                    json.dump(j, f, indent=4)

            # Push to remote
            rmtree(os.path.join(storage_path, data_path))
            copytree(data_path, os.path.join(storage_path, data_path))
            repo.git.add(os.path.join(data_path))
            repo.index.commit("New data")
            origin = repo.remote(name='origin')
            origin.push(branch)

            # Present text
            prep = "an" if chosen_role[0].lower() in ["a", "e", "i", "o", "u"] else "a"
            participant_text = f"We're happy to have you as {prep} {chosen_role} {roles[chosen_role]['emoji']}! "
                               #f"You can find more info on the event in your mailbox 📬"

            # TODO: Send email


    st.sidebar.markdown(f"**{participant_text}**")

    # Plot participants
    st.header("Vacancies")
    plot(df, roles)
    st.pyplot(transparent=True)
    
    st.header("Suggest or Vote on Next Papers")
    st.markdown("""Add your suggestions or vote on other papers [here](https://docs.google.com/spreadsheets/d/12fSacmB_gb4Wv7va20fRYooIpQSMuJkZ_7hDqW8k_t4/edit?usp=sharing)!""") 

    st.header("Contacts")
    st.markdown("""\t [MeetUp](https://www.meetup.com/pt-BR/Deep-Learning-Sessions-Lisboa/)"""
                """\t- [LinkedIn](https://www.linkedin.com/company/deeplisboa)"""
                """\t- [GitHub](https://github.com/DeepLearningLisbon)"""
                """\t- [Twitter](https://twitter.com/DeepLisboa)""")

def plot(df, roles):
    colors = [roles[role]["color"] for role in df["Role"].tolist()]

    fig, ax = plt.subplots(figsize=(5, 3.5))
    plt.barh(df["Role"].tolist(), df["Participants"].tolist(), color=colors, alpha=0.9, linewidth=8)
    plt.xticks(list(range(1+max([roles[role]["max_players"] for role in roles]))))

    # Beautify
    ax.spines['left'].set_color("#888888")
    ax.spines['bottom'].set_color("#888888")
    ax.xaxis.label.set_color('#888888')
    ax.yaxis.label.set_color('#888888')
    ax.tick_params(axis='x', colors='#888888')
    ax.tick_params(axis='y', colors='#888888')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_xlim(0, 4)
    # Add some space between the axis and the plot
    ax.spines['left'].set_position(('outward', 8))
    ax.spines['bottom'].set_position(('outward', 5))

    # Make some labels
    rects = ax.patches
    max_labels = [roles[role]["max_players"] for role in df["Role"].tolist()]
    n_labels = df["Participants"].tolist()
    labels = [f"{n}/{max}" for n, max in zip(n_labels, max_labels)]
    for rect, label, color in zip(rects, labels, colors):
        width = rect.get_width()
        ax.text(width + 0.1, rect.get_y() + rect.get_height() / 2, label,
                ha='left', va='center', color=color)


def validate_form(name, email, role, df):
    # Check role selected
    if role == "--Select--":
        return False, "⚠️ Please select your role before submiting"

    # Check evalid email
    if not is_email_valid(email):
        return False, f"⚠️ Please provide a valid email, \"{email}\" is not a valid email"

    # Check if email has no previous assigned role
    prev_role = get_role_by_email(df, email)
    if prev_role is not None:
        return False, f"⛔️ You have already chosen your role: {prev_role}"

    return True, None


def is_email_valid(text):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    return text is not None and len(text) > 0 and re.search(regex, text)


def get_role_by_email(participants_df, email):
    user_df = participants_df[participants_df["email"] == email]
    if len(user_df) > 0:
        return user_df.iloc[0]["role"]
    else:
        return None


if __name__ == '__main__':
    app_rg()

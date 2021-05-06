# Reading Group

Streamlit app that allows users to select which roles they want to play in the Reading Group.

![App look](images/outpy.gif)

To start the streamlit app run:

```
    streamlit run reading_group_roles.py
```

### Requirements
You'll need `streamlit=^0.80`, `pandas` and `matplotlib`.

### Storage
This app uses a git branch of this same repository as storage for small data: branch `data`. This avoids having 
to set up and maintain a separate data storage.

#### How to's
1. **How to know the participants submitted?** Got to [participants.json in the `data` branch](https://github.com/DeepLearningLisbon/reading-group/tree/data/data/participants.json)

2. **How to reset the participant counting?** Delete the data files, commit and push to the `data` branch.

####

### Secrets
If the data repo is private and you're running locally, then in order to run the app you need
[to generate a personal access token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) 
and add the file `.\streamlit\secrets.toml` with the following content:

```
github_token = "ghp_your_great_token"
```

If you're running on streamlit cloud [set your secrets in streamlit interface](https://blog.streamlit.io/secrets-in-sharing-apps/).
# gcp-stackdriver-agent-install
Installation of GCP agent for Stackdriver at all available hosts in GCP project
# How to Use (CentOS 7 with python3 and ssh keypair)

  0. Perform all necessary steps according to Google's [manual](https://cloud.google.com/monitoring/agent/install-agent)
  P.S. - rename generated JSON script for your project to **application_default_credentials.json**
  
  1. Place script at suitable directory
  2. Create file with any name you want(it'll be asked in script) & add all hosts where you want agent should be installed
  3. Get your user with ssh key that can perform sudo actions
  4. Run script: **`python3 install-GCP-agent.py`**
  5. Fulfill all entries for hosts file(use it local or enter absolute path), username and key for it(local or absolute path)
  6. Wait script to complete
  7. Re-run it to ensure that JSON is at place and agent was installed properly

# DcOps
This repository focuses Cisco ACI platform and its agenda is to create comprehensive application which provides ACI telemetory services, configuration implementations and daily DC operation activities.

## Requirments

#### Python version required
3.6+ works fine.

#### Modules required
mentioned in requirements.txt added in the folder

## Login information
Enter username, password andapic FQDN/ip address in Credentials.py file.

## Detailed EP mac address information

### get_ep_details2.py

get_ep_details(aci_cookie, apic_ip,mac_addr=None)
  
    Fetches EP details using API call

    Parameters:

    aci_cookie (dict): Session dictionary
    apic_ip (string): APIC controller ip address
    mac_address (string): (Optional) default is None. It searches specific mac-address

    Returns:
    dict: API response in JSON

  #### Running code
  python3 get_ep_details2.py
  
  #### input required
  ! To search all mac-addresses learned on ACI fabric leave input blank or enter mac address in format aa:bb:cc:dd:ee:ff to search specific mac address.
  
 
## End Notes
This appliction is under development and we are trying to improve it. Please let us know about your suggestions.
  

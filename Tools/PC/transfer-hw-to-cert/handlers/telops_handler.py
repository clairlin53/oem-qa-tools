'''
    TELOPS Jira Board Handler
'''

import json

from Jira.apis.base import JiraAPI


def create_send_dut_to_cert_card_in_telops(
        cqt_card: str,
        description_original_data: object,
        assignee_original_id: object,
        data: list
        ) -> None:
    """ Create card to TELOPS board for contractor using, the type of card is
        "DUT Send To Cert"

        @param:cqt_card, the key of the original card in CQT board.
            e.g. CQT-1234

        @param:reporter, the launchpad ID of someone QA.

        @param:data, a list contains CID information.
            e.g
                [
                    {
                        'CID': '202303-12345',
                        'Location': ''
                    },
                ]
    """
    issue_updates = []  # Put tasks in this list

    telops_jira_api = JiraAPI(
        path_of_jira_board_conf='./configs',
        jira_board_conf='jira_telops.json'
    )

    for d in data:
        # Template of "fields" payload in Jira's request
        fields = telops_jira_api.create_jira_fields_template(
            task_type='DUT_Send_To_Cert')

        # Assign Summary
        fields['summary'] = f"CID#{d['cid']} transferred to Cert Lab"

        # Assign Description
        fields['description'] = description_original_data

        # Assign Reporter
        fields['reporter']['id'] = assignee_original_id

        # Link task back to CQT task
        update_link = telops_jira_api.create_link_issue_content(
            target_issues=[{'key': cqt_card}])

        issue_updates.append({'fields': fields, 'update': update_link})
    response = telops_jira_api.create_issues(
        payload={'issueUpdates': issue_updates})

    if response.ok:
        print(json.dumps(response.json(), indent=2))
        print('Created the following cards to TELOPS board successfully')

        # Get the transition ID number which is from the TELOPS board
        transition_data = telops_jira_api.jira_project['transition_data']
        transition_id = transition_data.get('To Do Cert LAB')

        created_issues = response.json()['issues']

        for created_issue in created_issues:
            # Assign status with 'To Do Cert LAB'
            response = telops_jira_api.make_transition(
                created_issue['key'], transition_id)
    else:
        print('*' * 50)
        print(json.dumps(issue_updates, indent=2))
        raise Exception(
            'Error: Failed to create card to TELOPS board',
            f"Reason: {response.text}"
        )

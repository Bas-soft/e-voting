from django.shortcuts import render,redirect,get_object_or_404
from . models import Elections,Candidate,Portfolios,Voters,User,Votes
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login,logout, authenticate
from . forms import AddCandidateForm,AddVoters
from django.contrib import messages
import uuid
from django.utils import timezone
import pandas as pd
from django.conf import settings
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from django.middleware import csrf

from django.http import JsonResponse

# Create your views here.
def login_ToVote(request):
    if request.method == "POST":
        current_datetime = timezone.now()
        election = Elections.objects.filter(start_date__lte=current_datetime,
                                            end_date__gt=current_datetime).first()
        username = request.POST.get("username")
        password = request.POST.get("password")


        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)
            if user.is_superuser:
                return redirect("admin")
            else:
                if election:
                    # Voting is currently open
                    return redirect("Voting")
                else:
                    # Voting is closed
                    messages.success(request,"Please Contact the EC for info On Voting Time")
                    return redirect("_loging_")

        else:
            messages.success(request,"Sorry, You are not a valid voter. Please contact EC.")
            print("Sorry, You are not a valid voter. Please contact EC.")
            return redirect("_loging_")

    return render(request, "login.html")

def view_portfolio(request,portfolio):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            portfolio_condidates=Candidate.objects.filter(position=portfolio).order_by('-vote')
            get_portfolio_name = portfolio_condidates.first()
            portfolio_name = get_portfolio_name.position if get_portfolio_name else None
            count_candidtes=portfolio_condidates.count()

            get_election = get_object_or_404(Elections, id=1)  # Retrieve the Elections instance
            element_id = get_election

            voters = Voters.objects.filter(election=element_id)
            valid_voters = voters.count()

            votes=Votes.objects.filter(portfolio=portfolio)
            count_votes=votes.count()

            context={
                "candidates":portfolio_condidates,
                "portfolio":portfolio_name,
                "numb_candidates":count_candidtes,
                "numb_voters":valid_voters,
                "numb_votes":count_votes,
            }


            return render(request,"portfolios.html",context)
            pass
        else:
            return redirect("_loging_")
    else:
        return redirect("_loging_")

from django.contrib.auth.models import User

def import_data_from_excel(file_path):
    get_election = get_object_or_404(Elections, id=1)  # Retrieve the Elections instance
    element_id = get_election
    try:
        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(file_path)

        # Check if the required columns exist in the DataFrame
        required_columns = ['Name', 'Index number', 'personal contact']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing columns in the Excel file: {', '.join(missing_columns)}")

        # Iterate over the rows of the DataFrame
        for index, row in df.iterrows():
            generated_Token = str(uuid.uuid4())[:8]
            # Extract the necessary data from each row
            field1 = row['Name']  # Replace 'Name' with the column name from your Excel sheet
            field3 = row['personal contact']  # Replace 'personal contact' with the column name from your Excel sheet
            field2 = row['Index number']  # Replace 'Index number' with the column name from your Excel sheet

            if User.objects.filter(username=field2).exists():
                print("error,user alrady exists")
                # return redirect('voters')
            else:

                password = str(f"ATL{generated_Token.upper()}")

                # Create a new instance of your Django model and populate the fields
                obj = Voters(name=field1, index_number=field2.upper(), phone=field3, secret_token=password,election=element_id)

                # Save the object to the database
                obj.save()

                # Create a corresponding User object and set them as staff members
                user = User.objects.create_user(username=field2.upper(), password=password, is_staff=True)
                print("User created:", user.username)

        return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def process_excel_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')  # Get the uploaded file from the request


        # Specify the path to save the file temporarily
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)

        # Save the uploaded file temporarily
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Import data from the Excel file
        success = import_data_from_excel(file_path)

        if success:
            # Display a success message
            messages.success(request, "Data imported successfully.")
        else:
            # Display an error message
            messages.error(request, "Failed to import data.")

        # Delete the temporary file
        os.remove(file_path)

        return redirect('voters')

    return render(request, 'voters.html')


def view_voters(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            get_election = get_object_or_404(Elections, id=1)  # Retrieve the Elections instance
            element_id = get_election
            start_election = get_election.start_date
            end_election = get_election.end_date
            voters = Voters.objects.filter(election=element_id)
            valid_voters = voters.count()

            form = AddVoters()

            context = {
                "valid_voters": valid_voters,
                "election": get_election,
                "election_starts": start_election,
                "election_ends": end_election,
                "voters_form": form,
                "voters": voters,
            }
            voters=[[]]
            if request.method == "POST":
                generated_Token = str(uuid.uuid4())[:8]
                form = AddVoters(request.POST)
                if form.is_valid():
                    # Check if the user with the same username already exists
                    username = form.cleaned_data['index_number']
                    if User.objects.filter(username=username).exists():
                        messages.error(request, "Username already exists. Please choose a different username.")
                        #return redirect('voters')
                    else:

                        voter = form.save(commit=False)
                        voter.election = element_id  # Assign the Elections instance
                        voter.secret_token = f"ATL{generated_Token.upper()}"

                        # Create a user for this voter
                        password = str(f"ATL{generated_Token.upper()}")
                        user = User.objects.create_user(username=username, password=password, is_staff=True)
                        print("User created:", user.username)

                        voter.save()
                        messages.success(request, "Voter registered successfully.")
                        return redirect('voters')
                else:
                    messages.error(request, f"{form.errors}")
                    print(form.errors)

            return render(request, "voters.html", context)
        else:
            return redirect("_loging_")
    else:
        return redirect("_loging_")

def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            election = Elections.objects.all()
            get_election_name = election.first()
            election_name = get_election_name.title if get_election_name else None
            election_start = get_election_name.start_date if get_election_name else None
            election_end = get_election_name.end_date if get_election_name else None

            get_election = get_object_or_404(Elections, id=1)  # Retrieve the Elections instance
            element_id = get_election


            get_portfolios=Portfolios.objects.filter(election=element_id)
            portfolios_number=get_portfolios.count()

            get_candidates=Candidate.objects.filter(election=element_id)
            get_candidates_number =get_candidates.count()
            form = AddCandidateForm()




            context = {
                'elections': election_name,
                'elections_start': election_start,
                'elections_ends': election_end,
                'candidate_number': get_candidates_number,
                'candidate_form': form,
                'candidate_data': get_candidates,
                'portfolios': get_portfolios,
                'portfolios_number': portfolios_number,
            }

            if request.method == 'POST':
                form = AddCandidateForm(request.POST,request.FILES)
                if form.is_valid():
                    candidate = form.save(commit=False)
                    candidate.election = element_id  # Assign the Elections instance

                    candidate.save()
                    messages.success(request, "Candidate registered successfully.")
                    print("success")
                    return redirect('admin')
                else:
                    messages.error(request, f"{form.errors}")
                    print(form.errors)

            return render(request, 'dashboard.html', context)
        else:
            return redirect("_loging_")
    else:
        return redirect("_loging_")

from django.shortcuts import get_object_or_404

def viewVotePage(request):
    if request.user.is_authenticated:
        get_portfolios = Portfolios.objects.exclude(votes__user=request.user)
        portfolio_candidates = Candidate.objects.all()
        get_portfolio_name = portfolio_candidates.first()
        portfolio_name = get_portfolio_name.position if get_portfolio_name else None
        count_candidates = portfolio_candidates.count()

        context = {
            "portfolios": get_portfolios,
            "portfolio_candidates": portfolio_candidates,
            "numb_candidates": count_candidates,
        }

        current_datetime = timezone.now()

        try:
            election = Elections.objects.get(start_date__lte=current_datetime, end_date__gt=current_datetime)

            if request.method == 'POST':
                selected_candidates = request.POST.getlist('votes')

                current_user = request.user
                for selected_candidate in selected_candidates:
                    # Process the selected candidates' information
                    candidate_info = selected_candidate.split('|')
                    candidate_id = int(candidate_info[0])
                    candidate_number = candidate_info[1]
                    portfolio = candidate_info[2]

                    try:
                        candidate = Candidate.objects.get(id=candidate_id)
                        portfolio_instance = get_object_or_404(Portfolios, name_of_portfolio=portfolio)

                        if Votes.objects.filter(election=election, portfolio=portfolio_instance, user=current_user).exists():
                            messages.success(request, "You have already voted for this portfolio.")
                        else:
                            vote = Votes(election=election, portfolio=portfolio_instance, user=current_user, candidate=candidate)
                            vote.save()
                            candidate.vote += 1
                            candidate.save()
                            messages.success(request, f"You have successfully voted for {candidate.name} as {portfolio_instance}.")

                    except Candidate.DoesNotExist:
                        messages.success(request, "Please select a candidate to vote for.")
                        pass

            if not get_portfolios:
                messages.success(request, "You have voted for all portfolios.")

        except Elections.DoesNotExist:
            # No active election found
            messages.success(request, "Please contact the EC for information on voting time.")
            return redirect("_loging_")

        return render(request, "voting_page.html", context)
    else:
        messages.success(request, "You must be a valid voter to vote. Please contact the EC.")
        return redirect("_loging_")

def view_vote_Results(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            election = Elections.objects.all()
            get_election_name = election.first()
            election_name = get_election_name.title if get_election_name else None
            get_election = get_object_or_404(Elections, id=1)  # Retrieve the Elections instance
            element_id = get_election
            voters = Voters.objects.filter(election=element_id)
            valid_voters = voters.count()
            get_election = get_object_or_404(Elections, id=1)  # Retrieve the Elections instance
            element_id = get_election

            get_portfolios = Portfolios.objects.filter(election=element_id)
            portfolios_number = get_portfolios.count()

            get_candidates = Candidate.objects.filter(election=element_id)
            get_candidates_number = get_candidates.count()

            candidates = get_portfolios.first().candidate_set.all().order_by('-vote')
            highest_voted_candidate = candidates.first()

            context = {
                'elections': election_name,
                'candidate_number': get_candidates_number,
                'highest_voted_candidate': highest_voted_candidate,
                'candidate_data': get_candidates,
                'portfolios': get_portfolios,
                'portfolios_number': portfolios_number,
                'valid_voters': valid_voters,
            }

            return render(request, "vote_results.html", context)
        else:
            messages.success(request, "Please Contact Administrator!")
    else:
        messages.success(request, "You have to be logged in to access this page")

def contactUS(request):
    messages.success(request,"Call Bloom Administrative Systems  on 0544 022 765 / 0244 888 531")
    return redirect("_loging_")

def submitVotes(request,candidate_id):
    if request.method == 'POST':
        voted_candidate = Candidate.objects.filter(
            Candidate_Number__icontains=candidate_id
        )
        print("user ",request.user)
        # Process the candidate IDs and submit the votes to the model

        # Example: Increment the vote count for each candidate
        '''for candidate_id in candidate_ids:
            candidate = Candidate.objects.get(id=candidate_id)
            candidate.vote += 1
            candidate.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})'''

def log_out_user(request):
    logout(request)
    return redirect("_loging_")


def mNotify(number,message):
    import requests
    endPoint='https://api.mnotify.com/api/sms/quick'
    apiKey='ZVUzBl7eAA1HnDC0KeBPvK9Rs'
    data={
        'recipient[]':[number],
        'sender':'Bas_evote',
        'message':message,
        'is_schedule':False,
        'schedule_date':'',

    }
    url=endPoint +'?key='+apiKey

    response=requests.post(url,data)
    data=response.json()
    print(data)

def send_credentials(request):

    voters=Voters.objects.all()
    for voter in voters:
        sent_value = voter.sent_sms
        if not sent_value:
            try:
                phone_number = voter.phone  # Replace with the actual phone number field in your Voter model
                message = f"Your cred. for the ATL 2023/2024 Elections: Username: {voter.index_number}, \n \
                Password: {voter.secret_token} \n visit: https://bas-evote.herokuapp.com/atl-eVoting/login to vote"
    
                mNotify(int(phone_number), message)
                print(message)
                voter.sent_sms=True
                voter.save()

            except  Exception as e:
                print(f"An error occurred: {str(e)}")
        else:
            pass


    messages.success(request,"Credentials Sent Successfully!")

    return redirect("voters")
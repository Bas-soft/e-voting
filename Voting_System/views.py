from django.shortcuts import render,redirect,get_object_or_404
from . models import Elections,Candidate,Portfolios,Voters,User,Votes
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login,logout, authenticate
from . forms import AddCandidateForm,AddVoters
from django.contrib import messages
import uuid
from django.utils import timezone
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

            if request.method == "POST":
                generated_Token = str(uuid.uuid4())[:8]
                form = AddVoters(request.POST)
                if form.is_valid():
                    voter = form.save(commit=False)
                    voter.election = element_id  # Assign the Elections instance
                    voter.secret_token = f"ATL{generated_Token.upper()}"

                    # Create a user for this voter
                    username = form.cleaned_data['index_number']
                    password = str(f"ATL{generated_Token.upper()}")
                    user = User.objects.create_user(username=username, password=password,is_staff=True)
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

def viewVotePage(request):
    if request.user.is_authenticated:
        pass
        get_portfolios=Portfolios.objects.all()
        portfolio_condidates = Candidate.objects.all()
        get_portfolio_name = portfolio_condidates.first()
        portfolio_name = get_portfolio_name.position if get_portfolio_name else None
        count_candidtes = portfolio_condidates.count()

        context = {
            "portfolios": get_portfolios,
            "portfolio_candidates": portfolio_condidates,
            "numb_candidates": count_candidtes,
        }

        current_datetime = timezone.now()
        election = Elections.objects.filter(start_date__lte=current_datetime,
                                            end_date__gt=current_datetime).first()
        if election:
            if request.method == 'POST':
                candidate_ids = request.POST.getlist('candidate_ids[]')
                selected_candidates = request.POST.getlist('votes')
                print(selected_candidates)
                current_user = request.user


                for selected_candidate in selected_candidates:
                    # Process the candidate IDs and submit the votes to the model

                    candidate_info = selected_candidate.split('|')
                    candidate_id = int(candidate_info[0])
                    candidate_number = candidate_info[1]
                    portfolio = candidate_info[2]
                    election = candidate_info[3]


                #print(f'{candidate_id},{candidate_number},{portfolio},{election}')  # Process the selected candidates' numbers

                #use the candidate number too look for candidate's name
                try:
                    candidate_name=Candidate.objects.filter(id=int(candidate_id))
                    candidate=get_object_or_404(Candidate,id=candidate_id)
                    get_candidate_name = candidate_name.first()
                    #candidate_name = get_candidate_name.name if get_candidate_name else None
                    election_name = get_candidate_name.election if get_candidate_name else None


                    # Retrieve the portfolio instance
                    portfolio_instance = get_object_or_404(Portfolios, name_of_portfolio=portfolio)


                    if Votes.objects.filter(election=election_name,portfolio=portfolio_instance,user=current_user,).exists():
                        messages.success(request,"you have already voted for this portfolio")
                        print("you have already voted for this portfolio")
                    else:
                        print('vote')
                        vote=Votes(election=election_name,portfolio=portfolio_instance,user=current_user,candidate=get_candidate_name)
                        vote.save()
                        candidate.vote+=1
                        candidate.save()
                        messages.success(request, f"You've Successfully voted for {get_candidate_name} as {portfolio_instance}")

                except UnboundLocalError as e:
                    messages.success(request, "Please Select A Candidate To Vote For")
                    pass


            return render(request, "voting_page.html", context)
        else:
            # Voting is closed
            messages.success(request, "Please Contact the EC for info On Voting Time")
            return redirect("_loging_")

    else:
        messages.success(request,"You Must Be A Valid Voter To Vote, Please Contact The EC")
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
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models.signals import post_save
from card.models import *
from user.models import *
from document.models import *
import json
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

unit_tests = False
DECK_EXISTS_ERROR = -23

# Home page view
def home(request):
    #print request.user.username
    if request.user.is_active and request.user.is_authenticated:
        decks = Deck.objects.filter(owner=request.user)
        return render(request, 'index.html', {"decks": decks})
    return render(request, 'index.html', {})

def about(request):
    context = {}
    return render(request, 'about.html', context)

def report(request):
    context = {}
    return render(request, 'report.html', context)

def get_all_cards(request):
    cards = Card.objects.all()
    cards_output = serializers.serialize("json", cards)
    return JsonResponse(cards_output, safe=False)

# Return all cards of a company, given company name
# def get_company_cards(request):
#     company_name = request.GET.get('company_name')
#     cards = Card.objects.filter(associated_company=company_name)
#     cards_output = serializers.serialize("json", cards)
#     return JsonResponse(cards_output, safe=False)

#############################
# NEW DECK AND CARDS DESIGN #
#############################

# Add card given company name, status, tags, and contact info
@csrf_exempt
def create_deck(request):
    if unit_tests:
        company_name = request.POST['companyName']
        company_description = request.POST['companyDescription']
    else:
        info = json.loads(request.POST.keys()[0])
        company_name = info['companyName']
        company_description = info['companyDescription']

    user = UserProfile.objects.get(username=request.user)

    try:
        company = Company.objects.get(name=company_name)
    except Company.DoesNotExist:
        company = Company(name=company_name, description=company_description)
        company.save()

    try:
        Deck.objects.get(associated_company=company, owner=user)
        response = {'error_message': DECK_EXISTS_ERROR}
        return JsonResponse(response, safe=False)
    except Deck.DoesNotExist:
        new_deck = Deck(associated_company=company, owner=user)
        new_deck.save()

    deck_id = str(new_deck.unique_id)
    response = {'deck_id': deck_id, 'error_message': 1}
    return JsonResponse(response, safe=False)

 #Adding a position to the deck
@csrf_exempt
def add_card(request):
    if unit_tests:
        info = request.POST
    else:
        info = json.loads(request.POST.keys()[0])
    deck_id = info['deck_id']
    deck = Deck.objects.get(unique_id=deck_id)
    job_title = info['jobTitle']
    status = str(info['status'])
    notes = str(info['notes'])
    tags = str(info['tags']).split(',')
    contact_name = str(info['contactName'])
    contact_email = str(info['contactEmail'])
    contact_phone = str(info['contactPhone'])

    new_card = Card(job_title=job_title, status=status, notes=notes, card_deck=deck)
    new_card.save()

    new_contact = Contact(name=contact_name, phone=contact_phone, email=contact_email, associated_card=new_card)
    new_contact.save()

    for tag in tags:
        new_tag = Tag(tag=tag.strip(), tagged_card=new_card)
        new_tag.save()
    card_id = str(new_card.card_id)
    response = {'card_id': card_id, 'error_message': 1}
    return JsonResponse(response, safe=False)

# Remove deck, given a deck id
@csrf_exempt
def delete_deck(request):
    try:
        if unit_tests:
            deck_id = request.POST['deck_id']
        else:
            info = json.loads(request.POST.keys()[0])
            deck_id = info['deck_id']
        Deck.objects.get(unique_id=deck_id).delete()
        return JsonResponse({'error_message': 1}, safe=False)
    except Deck.DoesNotExist:
        return JsonResponse({'error_message': -22}, safe=False)

# Remove card, given a card id
@csrf_exempt
def remove_card(request):
    try:
        if unit_tests:
            card_id = request.POST['card_id']
        else:
            info = json.loads(request.POST.keys()[0])
            card_id = info['card_id']
        Card.objects.get(card_id=card_id).delete()
        return JsonResponse({'error_message': 1}, safe=False)
    except Card.DoesNotExist:
        return JsonResponse({'error_message': -8}, safe=False)

###################
# CARD ATTRIBUTES #
###################

# Return the contact information in JSON given a card ID
def get_contacts(request):
    card_id = request.GET.get('card_id')
    card = Card.objects.filter(card_id=card_id)
    contacts = Contact.objects.all().filter(associated_card=card)
    contacts_output = serializers.serialize("json", contacts)
    return JsonResponse(contacts_output, safe=False)

# Remove contact, given a card id and contact name
def remove_contact(request):
    try:
        if unit_tests:
            card_id = request.POST['card_id']
            contact_name = request.POST['contactName']
        else:
            info = json.loads(request.POST.keys()[0])
            card_id = info['card_id']
            contact_name = info['contact_name']

        card = Card.objects.get(card_id=card_id)
        Contact.objects.get(name=contact_name, associated_card=card).delete()
        return JsonResponse({'error_message': 1}, safe=False)
    except Card.DoesNotExist:
        return JsonResponse({'error_message': -8}, safe=False)
    except Contact.DoesNotExist:
        return JsonResponse({'error_message': -14}, safe=False)

# Edit a contact, given a card id and contact fields (not all fields may be overridden, depending on what user edits)
@csrf_exempt
def edit_contact(request):
    try:
        if unit_tests:
            card_id = request.POST['card_id']
            new_name = request.POST['new_name']
            new_email = request.POST['new_email']
            new_phone = request.POST['new_phone']
            current_name = request.POST['current_name']
        else:
            info = json.loads(request.POST.keys()[0])
            card_id = info['card_id']
            new_name = info['new_name']
            new_email = info['new_email']
            new_phone = info['new_phone']
            current_name = info['current_name']
        card = Card.objects.get(card_id=card_id)
        contact = Contact.objects.get(name=current_name, associated_card=card)
        contact.name = new_name
        contact.email = new_email
        contact.phone = new_phone
        contact.save()
        return JsonResponse({'error_message': 1}, safe=False)
    except Card.DoesNotExist:
        return JsonResponse({'error_message': -8}, safe=False)
    except Contact.DoesNotExist:
        return JsonResponse({'error_message': -14}, safe=False)

# Add contact given card id and contact info
@csrf_exempt
def add_contact(request):
    try:
        if unit_tests:
            card_id = request.POST['card_id']
            add_name = request.POST['add_name']
            add_email = request.POST['add_email']
            add_phone = request.POST['add_phone']
        else:
            info = json.loads(request.POST.keys()[0])
            card_id = info['card_id']
            add_name = info['add_name']
            add_email = info['add_email']
            add_phone = info['add_phone']
        card = Card.objects.get(card_id=card_id)
        add_contact = Contact(name= "," + add_name, email=add_email, phone=add_phone, associated_card=card)
        add_contact.save()
        return JsonResponse({'error_message': 1}, safe=False)
    except Card.DoesNotExist:
        return JsonResponse({'error_message': -8}, safe=False)
    except Contact.DoesNotExist:
        return JsonResponse({'error_message': -14}, safe=False)

#######################################################################

# Add tags based on card id and tag names
@csrf_exempt
def add_tag(request):
    if unit_tests:
        card_id = request.POST['card_id']
        card = Card.objects.get(card_id=card_id)
        tags = request.POST['tags'].split(',')
    else:
        info = json.loads(request.POST.keys()[0])
        card_id = info['card_id']
        card = Card.objects.get(card_id=card_id)
        tags = info['tags'].split(',')

    for tag in tags:
        new_tag = Tag(tag=tag, tagged_card=card)
        new_tag.save()
    return JsonResponse({'error_message': 1}, safe=False)

# Remove tag or set of tags, given a card id and tag name(s)
@csrf_exempt
def remove_tag(request):
    try:
        if unit_tests:
            card_id = request.POST['card_id']
            target_tag = request.POST['target_tag']
        else:
            info = json.loads(request.POST.keys()[0])
            card_id = info['card_id']
            target_tag = info['target_tag']

        card = Card.objects.get(card_id=card_id)
        Tag.objects.get(tagged_card=card, tag=target_tag).delete()
        return JsonResponse({'error_message': 1}, safe=False)
    except Card.DoesNotExist:
        return JsonResponse({'error_message': -8}, safe=False)
    except Tag.DoesNotExist:
        return JsonResponse({'error_message': -3}, safe=False)

# Get all tags associated with a card id
def get_tags(request):
    try:
        card_id = request.GET.get('card_id')
        card = Card.objects.get(card_id=card_id)
        tags = Tag.objects.all().filter(tagged_card=card)
        tags_output = serializers.serialize("json", tags)
        return JsonResponse(tags_output, safe=False)
    except Card.DoesNotExist:
        return JsonResponse({'error_message': -8}, safe=False)
    except Tag.DoesNotExist:
        return JsonResponse({'error_message': -3}, safe=False)

# Modify a tag, given a card id and tag name
@csrf_exempt
def edit_tag(request):
    try:
        if unit_tests:
            card_id = request.POST['card_id']
            tag_to_replace = request.POST['tag_to_replace']
            new_tag = request.POST['new_tag']
        else:
            info = json.loads(request.POST.keys()[0])
            card_id = info['card_id']
            tag_to_replace = info['tag_to_replace']
            new_tag = info['new_tag']
        card = Card.objects.get(card_id=card_id)
        target = Tag.objects.get(tagged_card=card, tag=tag_to_replace)
        target.tag = new_tag
        target.save()
        return JsonResponse({'error_message': 1}, safe=False)
    except Card.DoesNotExist:
        return JsonResponse({'error_message': -8}, safe=False)

#######################################################################

# Change status based on card id and new status
@csrf_exempt
def modify_card_status(request):
    try:
        if unit_tests:
            card_id = request.POST['card_id']
            new_status = request.POST['new_status']
        else:
            info = json.loads(request.POST.keys()[0])
            card_id = info['card_id']
            new_status = info['new_status']

        card = Card.objects.get(card_id=card_id)
        card.status = new_status
        card.save()
        return JsonResponse({'error_message': 1}, safe=False)
    except Card.DoesNotExist:
        return JsonResponse({'error_message': -8}, safe=False)
    return JsonResponse({'error_message': 1}, safe=False)

#######################################################################

# Edit the notes for a company.
@csrf_exempt
def edit_notes(request):
    try:
        if unit_tests:
            card_id = request.POST['card_id']
            new_notes = request.POST['new_notes']
        else:
            info = json.loads(request.POST.keys()[0])
            card_id = info['card_id']
            new_notes = info['new_notes']

        card = Card.objects.get(card_id=card_id)
        card.notes = new_notes
        card.save()
        return JsonResponse({'error_message': 1}, safe=False)
    except Card.DoesNotExist:
        return JsonResponse({'error_message': -8}, safe=False)

#######################################################################

@csrf_exempt
def add_task(request):
    try:
        if unit_tests:
            card_id = request.POST['card_id']
            new_task = request.POST['new_task']
        else:
            info = json.loads(request.POST.keys()[0])
            card_id = info['card_id']
            new_task = info['new_task']
        card = Card.objects.get(card_id=card_id)
        add_task = Task(task=new_task, associated_card=card)
        add_task.save()
        return JsonResponse({'error_message': 1}, safe=False)
    except Task.Exception:
        return JsonResponse({'error_message': -16}, safe=False)

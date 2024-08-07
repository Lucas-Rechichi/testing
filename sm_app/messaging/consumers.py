import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sm_app.settings')
import django
django.setup()

import json
import pytz
from main.models import UserStats, Notification
from main.extras import remove_until_character
from messaging.extras import replace_spaces
from messaging.models import ChatRoom, Message, PollMessage, PollOption, PollingChoice
from django.contrib.auth.models import User

from channels.generic.websocket import WebsocketConsumer

from asgiref.sync import async_to_sync


class MessageConsumer(WebsocketConsumer):
    def connect(self):
        # Collects relevant information about the chatroom.
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        user = self.scope["user"]

        # Getting relevant database objects
        chat_room = ChatRoom.objects.get(id=self.room_id)
        user_stats = UserStats.objects.get(user=user)

        # Defining the room name
        self.room_group_name = f'chat_room_{self.room_id}_{replace_spaces(string=chat_room.name, replacement="_")}'

        # Checking to see if this user has been invited to the chatroom.
        if chat_room.users.filter(user=user_stats.user).exists():
            # Add the user to the channel layer
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            # Accept the WebSocket connection
            self.accept()
        else:
            # Take action if the user is not on the specific page or is not allowed in the chatroom
            self.close(code=4001)  # Close the connection with a custom error code

    def disconnect(self, close_code):
        # Remove the WebSocket from the group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # Accessing sent data
        text_data_json = json.loads(text_data)
        user = self.scope.get("user")  # Use get to safely get the user who is on the page

        # Getting universal data across all 3 message types
        message_type = text_data_json['message_type']
        message_id = text_data_json['message_id']
        is_reply = text_data_json['is_reply']

        message = Message.objects.get(id=message_id)

        # Getting specific data for message types
        if message_type == 'text':
            content = message.text
        elif message_type == 'image':
            content = message.image.url
        elif message_type == 'video':
            content = message.video.url
        elif message_type == 'audio':
            content = message.audio.url
        else:
            print('invalid message type')
        
        # Getting unique data for a reply message
        if is_reply == 'true':
            reply_id = text_data_json['reply_id']
        else:
            reply_id = None
        

        if user and user.is_authenticated:
            # Send the message to the group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_type': message_type,
                    'content': content,
                    'message_id': message_id,
                    'is_reply': is_reply,
                    'reply_id': reply_id,
                    'username': user.username,
                }
            )
    
    def chat_message(self, event):
        # Accessing sent data
        content = event['content']
        message_type = event['message_type']
        message_id = event['message_id']
        is_reply = event['is_reply']
        reply_id = event['reply_id']
        username = event['username']

        # Getting relevant database objects
        user = User.objects.get(username=username)
        user_stats = UserStats.objects.get(user=user)
        user_pfp_url = user_stats.pfp.url
        
        # Formatting of the timezone when message is displayed on the screen
        local_timezone = pytz.timezone("Australia/Sydney")
        local_datetime = Message.objects.latest('sent_at').sent_at.astimezone(local_timezone)
        formatted_datetime = local_datetime.strftime("%B %d, %Y, %I:%M %p").lower().replace('am', 'a.m.').replace('pm', 'p.m.')
        formatted_datetime_capitalized = formatted_datetime.capitalize()
        
        # Sending relevant data over
        if message_type == 'text':
            content_html = f'<p>{content}</p>'
            self_reply_button_html = f'<button type="button" class="btn reply" data-message-id="{message_id}" data-message="{content}" data-message-sender="{username}""><i class="bi bi-reply" style="color: #ffffff;"></i></button>'
            other_reply_button_html = f'<button type="button" class="btn reply" data-message-id="{message_id}" data-message="{content}" data-message-sender="{username}""><i class="bi bi-reply"></i></button>'
            if is_reply == 'true':
                reply_message = Message.objects.get(id=reply_id)
                if reply_message.text:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0">{reply_message.text}</p></a>'
                elif reply_message.image:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0"><strong>Image</strong></p></a>'
                else:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0"><strong>Video</strong></p></a>'
                self.send(text_data=json.dumps({
                    'type': 'incoming_reply_message',
                    'message_type': message_type,
                    'content_html':content_html,
                    'message_id': message_id,
                    'is_reply': is_reply,
                    'reply_message_user': reply_message.sender.user.username,
                    'reply_id': reply_message.pk,
                    'reply_html': reply_html,
                    'self_reply_button_html': self_reply_button_html,
                    'other_reply_button_html': other_reply_button_html,
                    'username': user.username,
                    'sent_at': formatted_datetime_capitalized,
                    'user_pfp_url': user_pfp_url
                }))
            else:
                self.send(text_data=json.dumps({
                    'type': 'incoming_message',
                    'message_type': message_type,
                    'content_html':content_html,
                    'message_id': message_id,
                    'is_reply': is_reply,
                    'self_reply_button_html': self_reply_button_html,
                    'other_reply_button_html': other_reply_button_html,
                    'username': user.username,
                    'sent_at': formatted_datetime_capitalized,
                    'user_pfp_url': user_pfp_url
                }))
        elif message_type == 'image':
            content_html = f'<img src="{content}" alt="" class="mt-1" style="width: 100%; height:88%; border-radius: 5px;">'
            self_reply_button_html = f'<button type="button" class="btn reply" data-message-id="{message_id}" data-message="Image" data-message-sender="{username}""><i class="bi bi-reply" style="color: #ffffff;"></i></button>'
            other_reply_button_html = f'<button type="button" class="btn reply" data-message-id="{message_id}" data-message="Image" data-message-sender="{username}""><i class="bi bi-reply"></i></button>'
            if is_reply == 'true':
                reply_message = Message.objects.get(id=reply_id)
                if reply_message.text:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0">{reply_message.text}</p></a>'
                elif reply_message.image:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0"><strong>Image</strong></p></a>'
                else:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0"><strong>Video</strong></p></a>'
                self.send(text_data=json.dumps({
                    'type': 'incoming_reply_message',
                    'message_type': message_type,
                    'content_html':content_html,
                    'message_id': message_id,
                    'is_reply': is_reply,
                    'reply_message_user': reply_message.sender.user.username,
                    'reply_id': reply_message.pk,
                    'reply_html': reply_html,
                    'self_reply_button_html': self_reply_button_html,
                    'other_reply_button_html': other_reply_button_html,
                    'username': user.username,
                    'sent_at': formatted_datetime_capitalized,
                    'user_pfp_url': user_pfp_url
                }))
            else:
                self.send(text_data=json.dumps({
                    'type': 'incoming_message',
                    'message_type': message_type,
                    'content_html':content_html,
                    'message_id': message_id,
                    'is_reply': is_reply,
                    'self_reply_button_html': self_reply_button_html,
                    'other_reply_button_html': other_reply_button_html,
                    'username': user.username,
                    'sent_at': formatted_datetime_capitalized,
                    'user_pfp_url': user_pfp_url
                }))
        elif message_type == 'video':
            content_html = f'<video src="{content}" controls class="mt-1" style="width: 100%; height:88%; border-radius: 5px;"></video>'
            self_reply_button_html = f'<button type="button" class="btn reply" data-message-id="{message_id}" data-message="Video" data-message-sender="{username}""><i class="bi bi-reply" style="color: #ffffff;"></i></button>'
            other_reply_button_html = f'<button type="button" class="btn reply" data-message-id="{message_id}" data-message="Video" data-message-sender="{username}""><i class="bi bi-reply"></i></button>'
            if is_reply == 'true':
                reply_message = Message.objects.get(id=reply_id)
                if reply_message.text:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0">{reply_message.text}</p></a>'
                elif reply_message.image:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0"><strong>Image</strong></p></a>'
                else:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0"><strong>Video</strong></p></a>'
                self.send(text_data=json.dumps({
                    'type': 'incoming_reply_message',
                    'message_type': message_type,
                    'content_html':content_html,
                    'message_id': message_id,
                    'is_reply': is_reply,
                    'reply_message_user': reply_message.sender.user.username,
                    'reply_id': reply_message.pk,
                    'reply_html': reply_html,
                    'self_reply_button_html': self_reply_button_html,
                    'other_reply_button_html': other_reply_button_html,
                    'username': user.username,
                    'sent_at': formatted_datetime_capitalized,
                    'user_pfp_url': user_pfp_url
                }))
            else:
                self.send(text_data=json.dumps({
                    'type': 'incoming_message',
                    'message_type': message_type,
                    'content_html':content_html,
                    'message_id': message_id,
                    'is_reply': is_reply,
                    'self_reply_button_html': self_reply_button_html,
                    'other_reply_button_html': other_reply_button_html,
                    'username': user.username,
                    'sent_at': formatted_datetime_capitalized,
                    'user_pfp_url': user_pfp_url
                }))

        elif message_type == 'audio':
            content_html = f'<audio src="{content}" controls class="mt-1"></audio>'
            self_reply_button_html = f'<button type="button" class="btn reply" data-message-id="{message_id}" data-message="Video" data-message-sender="{username}""><i class="bi bi-reply" style="color: #ffffff;"></i></button>'
            other_reply_button_html = f'<button type="button" class="btn reply" data-message-id="{message_id}" data-message="Video" data-message-sender="{username}""><i class="bi bi-reply"></i></button>'
            if is_reply == 'true':
                reply_message = Message.objects.get(id=reply_id)
                if reply_message.text:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0">{reply_message.text}</p></a>'
                elif reply_message.image:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0"><strong>Image</strong></p></a>'
                else:
                    reply_html = f'<a href="#message-{reply_message.pk}" class="btn p-0"><p class="small text-truncate m-0"><strong>Video</strong></p></a>'
                self.send(text_data=json.dumps({
                    'type': 'incoming_reply_message',
                    'message_type': message_type,
                    'content_html':content_html,
                    'message_id': message_id,
                    'is_reply': is_reply,
                    'reply_message_user': reply_message.sender.user.username,
                    'reply_id': reply_message.pk,
                    'reply_html': reply_html,
                    'self_reply_button_html': self_reply_button_html,
                    'other_reply_button_html': other_reply_button_html,
                    'username': user.username,
                    'sent_at': formatted_datetime_capitalized,
                    'user_pfp_url': user_pfp_url
                }))
            else:
                self.send(text_data=json.dumps({
                    'type': 'incoming_message',
                    'message_type': message_type,
                    'content_html':content_html,
                    'message_id': message_id,
                    'is_reply': is_reply,
                    'self_reply_button_html': self_reply_button_html,
                    'other_reply_button_html': other_reply_button_html,
                    'username': user.username,
                    'sent_at': formatted_datetime_capitalized,
                    'user_pfp_url': user_pfp_url
                }))
        else:
            print('Invalid message type.')

class NotificationConsumer(WebsocketConsumer):
    connected_users = {}

    def connect(self):
        self.room_group_names = [] # keeps track of all of the chatrooms that will be connected to

        user = self.scope["user"] # gets user acessing the consumer class

        user_stats = UserStats.objects.get(user=user)
        chat_rooms = ChatRoom.objects.filter(users=user_stats) # gets all chatrooms that the user is invited in
        self.connected_users[self.channel_name] = user_stats.user

        for chat_room in chat_rooms:  
            self.room_group_name = f'notification-stream-{chat_room.pk}' # name is unique to the chatroom's id
            self.room_group_names.append(self.room_group_name)
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            
        self.accept() # connect
            

    def disconnect(self, close_code):
        self.connected_users.pop(self.channel_name)
        for room_name in self.room_group_names: # loops though all connected chatrooms
            async_to_sync(self.channel_layer.group_discard)(
                room_name,
                self.channel_name
            )

    def receive(self, text_data):

        # getting relevant data over to the consumer class
        text_data_json = json.loads(text_data)
        notification_ids = text_data_json['notification_ids']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_notification',
                'notification_ids': notification_ids,
            }
        )

    def chat_notification(self, event):
        notification_ids = event['notification_ids']
        for notification_id in notification_ids:
            notification = Notification.objects.get(id=notification_id)
            if notification.user.user.username == self.connected_users[self.channel_name].username:
                new_notification = notification
                sender_userstats = UserStats.objects.get(user=User.objects.get(username=new_notification.sender))

                # For the datetime such that it looks neater when displayed
                local_timezone = pytz.timezone("Australia/Sydney")
                local_datetime = new_notification.time_stamp.astimezone(local_timezone)
                formatted_datetime = local_datetime.strftime("%B %d, %Y, %I:%M %p").lower().replace('am', 'a.m.').replace('pm', 'p.m.')
                formatted_datetime_capitalized = formatted_datetime.capitalize()
                notification_timestamp = formatted_datetime_capitalized

                # For the notification icon
                notification_count = Notification.objects.filter(user=new_notification.user).count()

                # Formatting of the notification content for image and video responses as well as replies from them as well.
                if new_notification.relevant_message:
                    if new_notification.relevant_message.text:
                        notification_contents  = f'<p class="text-truncate ">{new_notification.contents}</p>'
                    else:
                        if new_notification.relevant_message.reply:
                            contents = remove_until_character(new_notification.contents, ':')
                            contents_a = remove_until_character(contents, ' ')
                            notification_contents  = f'<p class="text-truncate ">({new_notification.sender} Replied to You): <strong>{contents_a}</strong></p>'
                        else:
                            notification_contents  = f'<p class="text-truncate "><strong>{new_notification.contents}</strong></p>'
                else: # for poll messages
                    notification_contents = f'<p class="text-truncate "><strong>Poll: </strong>{new_notification.contents}</p>'
                print(notification_contents)
                html_notification_popup = f'''
                <div id="popup-notification-{new_notification.pk}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header">
                        <button class="btn p-0" onclick="location.href='/chat/{new_notification.source.name}/{new_notification.source.pk}'" id="read-notification-{new_notification.pk}">
                            <img src="{new_notification.source.icon.url}" class="rounded me-2" alt="..." style="height: 2.5rem; width: 2.5rem">
                        </button>
                        <button class="btn p-0 pe-2" onclick="location.href='/chat/{new_notification.source.name}/{new_notification.source.pk}'" id="read-notification-{new_notification.pk}">
                            <strong class="me-auto">{new_notification.source.name}</strong>
                        </button>
                        <small class="text-muted pe-2">just now</small>
                        <button type="button ms-2" class="btn-close" id="close-notification-{new_notification.pk}" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        <div class="row">
                            <div class="col">
                                <img src="{sender_userstats.pfp.url}" class="rounded me-2" alt="" style="height: 2.5rem; width: 2.5rem">
                                <em>{sender_userstats.user.username}</em>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col mt-2">
                                {notification_contents}
                            </div>
                        </div>
                    </div>
                </div>
                '''

                stored_html_notification = f'''
                <div id="stored-notification-{new_notification.pk}" class="card mb-2" aria-live="assertive" aria-atomic="true" data-bs-autohide="false">
                    <div class="card-header">
                        <button class="btn p-0" onclick="location.href='/chat/{new_notification.source.name}/{new_notification.source.pk}'" id="read-notification-{new_notification.pk}">
                            <img src="{new_notification.source.icon.url}" class="rounded me-2" alt="" style="height: 2.5rem; width: 2.5rem">
                        </button>
                        <button class="btn p-0 pe-2"  onclick="location.href='/chat/{new_notification.source.name}/{new_notification.source.pk}'" id="read-notification-{new_notification.pk}">
                            <strong class="me-auto">{new_notification.source.name}</strong>
                        </button>
                        <small class="text-muted pe-2">{notification_timestamp}</small>
                        <button type="button ms-2" class="btn-close" id="close-notification-{new_notification.pk}" aria-label="Close"></button>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col">
                                <img src="{sender_userstats.pfp.url}" class="rounded me-2" alt="" style="height: 2.5rem; width: 2.5rem">
                                <em>{sender_userstats.user.username}</em>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col mt-2">
                                {notification_contents}
                            </div>
                        </div>
                    </div>
                </div>
                '''
                notification_id = new_notification.pk

                self.send(text_data=json.dumps({
                    'type': 'incoming_notification',
                    'html_notification_popup': html_notification_popup,
                    'stored_html_notification': stored_html_notification,
                    'notification_id': notification_id,
                    'notification_count': notification_count,
                    'receiver': new_notification.user.user.username,
                    'source_name': new_notification.source.name,
                }))

class EventConsumer(WebsocketConsumer):
    def connect(self):
        # Collects relevant information about the chatroom.
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        user = self.scope["user"]

        # Getting relevant database objects
        chat_room = ChatRoom.objects.get(id=self.room_id)
        user_stats = UserStats.objects.get(user=user)

        # Defining the room name
        self.room_group_name = f'event_room_{self.room_id}'

        # Checking to see if this user has been invited to the chatroom.
        if chat_room.users.filter(user=user_stats.user).exists():
            # Add the user to the channel layer
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            # Accept the WebSocket connection
            self.accept()
        else:
            # Take action if the user is not on the specific page or is not allowed in the chatroom
            self.close(code=4001)  # Close the connection with a custom error code

    def disconnect(self, close_code):
        # Remove the WebSocket from the group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event_type = text_data_json['event_type']

        user = self.scope.get("user")

        if event_type == 'create_poll':
            poll_id = text_data_json['poll_id']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'event_manager',
                    'event_type': event_type,
                    'poll_id': poll_id,
                    'sender': user.username,
                }
            )
        elif event_type == 'vote_for_poll':
            option_id = text_data_json['option_id']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'event_manager',
                    'event_type': event_type,
                    'option_id': option_id,
                    'voter': user.username,
                }
            )
    
    def event_manager(self, event):
        event_type = event['event_type']

        if event_type == 'create_poll':
            poll_id = event['poll_id']

            poll = PollMessage.objects.get(id=poll_id)
            poll_title = poll.title

            # For the datetime such that it looks neater when displayed
            local_timezone = pytz.timezone("Australia/Sydney")
            local_datetime = poll.sent_at.astimezone(local_timezone)
            formatted_datetime = local_datetime.strftime("%B %d, %Y, %I:%M %p").lower().replace('am', 'a.m.').replace('pm', 'p.m.')
            formatted_datetime_capitalized = formatted_datetime.capitalize()
            poll_sent_at = formatted_datetime_capitalized

            options = []
            for option in poll.options.all():
                options.append({
                    'option_name': option.option,
                    'option_id': option.pk,
                })
            option_count = len(options)

            sender = event['sender']
            user = User.objects.get(username=sender)
            user_pfp_url = UserStats.objects.get(user=user).pfp.url 

            self.send(text_data=json.dumps({
                    'type': 'incoming_poll_message',
                    'poll_title': poll_title,
                    'poll_id': poll_id,
                    'poll_sent_at': poll_sent_at,
                    'options': options,
                    'option_count': option_count,
                    'sender': sender,
                    'sender_pfp_url': user_pfp_url
                }))
            
        elif event_type == 'vote_for_poll':
            option_id = event['option_id']

            voter = event['voter']
            voter_user = User.objects.get(username=voter)
            voter_userstats = UserStats.objects.get(user=voter_user)
            option = PollOption.objects.get(id=option_id)
            
            poll_title = option.poll.title
            poll_id = option.poll.pk
            poll_sender = option.poll.sender.user.username
            option_count = option.poll.options.all().count()

            options_list = []
            total_votes = 0
            for option_y in option.poll.options.all():
                total_votes += option_y.choices.all().count()
            
            for option_x in option.poll.options.all():
                amount_of_votes = option_x.choices.all().count()
                vote_percent = (amount_of_votes / total_votes) * 100
                choice_voters = []
                for choice_x in option_x.choices.all():
                    choice_voters.append({
                        'voter': choice_x.voter.user.username,
                    })
                options_list.append({
                    'option_name': option_x.option,
                    'option_id': option_x.pk,
                    'amount_of_votes': amount_of_votes,
                    'voters': choice_voters,
                    'vote_percent': round(vote_percent, 1),
                })

            self.send(text_data=json.dumps({
                    'type': 'incoming_poll_vote',
                    'poll_title': poll_title,
                    'poll_sender': poll_sender,
                    'poll_id': poll_id,
                    'voted_for_option_id': option_id,
                    'has_chosen': option.poll.has_voted(voter_userstats),
                    'voter': voter,
                    'options': options_list, 
                    'option_count': option_count,
                }))

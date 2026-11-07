Contents of https://forum.proxmox.com/threads/api-token-config.92465/:
# \[SOLVED\] - API Token config

* [#1](/threads/api-token-config.92465/post-402670)

Hi,

I'm new to the API world. But with what I've been able to do so far, I'm a fan!!

I have been able to work with the UserCredential/Ticket auth method.  
Reusing the AuthCookie and Csrfpreventiontoken. All good.  
I made a few scripts to automate some actions, and it's working fine.

Now I would like to go to the next step, skip this ticket request and use the API token for Auth.  
But it's giving me data=null !  
[![screenshot.35.jpg](https://forum.proxmox.com/data/attachments/27/27314-a60811764c29faa22db7a0ff8749629f.jpg?hash=pggRdkwp-q "screenshot.35.jpg")](https://forum.proxmox.com/attachments/screenshot-35-jpg.27618/)

I'm passing the token as an Authorization value in the header. But I'm missing something.  
Could you help me?  
thank you.

Veeh

[![fabian](/data/avatars/s/35/35714.jpg?1475744556)](/members/fabian.35714/)

* [#2](/threads/api-token-config.92465/post-402763)

just to make sure - the "TOKENID" in your screenshot is you censoring your API token secret? ![;)](https://cdn.jsdelivr.net/joypixels/assets/8.0/png/unicode/64/1f609.png "Wink    ;)") if not, you need to put the secret that got displayed when generating the token in its place..

do you see anything in the logs of the PVE host? `journalctl -u pveproxy -u pvedaemon -f` and repeat your attempt..

#### [Veeh](/members/veeh.47821/)

##### Well-Known Member

* [#3](/threads/api-token-config.92465/post-402973)

Hello,

Thank you fabian. Sorry about the misleading screenshot, but yes "TOKENID" was the token secret.  
I could not see anything in the log when running the query.  
Where I usually get "successful auth for user 'api@pve'" (When using a ticket)  
So I created a new token for the same user and it worked!

Weird, when the info is wrong the request returns a 401 invalid user/token...  
the data:null threw me off, I should have tried with another token way sooner.  
thanks.  
Have a nice day

Edit: I realized something, I had "privilege separation" enable with the first token. Not the new one.  
So I created another one to test this, and that's it. With privilege separation enable, I get data:null as a response.  
You can disable it afterward, and it's working fine.  
I presume this function is there to disable a token without removing it?  
It's enabled by default though.

Last edited: Jul 13, 2021

[![fabian](/data/avatars/s/35/35714.jpg?1475744556)](/members/fabian.35714/)

* [#4](/threads/api-token-config.92465/post-403263)

> Hello,
>
> Thank you fabian. Sorry about the misleading screenshot, but yes "TOKENID" was the token secret.  
> I could not see anything in the log when running the query.  
> Where I usually get "successful auth for user 'api@pve'" (When using a ticket)  
> So I created a new token for the same user and it worked!
>
> Weird, when the info is wrong the request returns a 401 invalid user/token...  
> the data:null threw me off, I should have tried with another token way sooner.  
> thanks.  
> Have a nice day
>
> Edit: I realized something, I had "privilege separation" enable with the first token. Not the new one.  
> So I created another one to test this, and that's it. With privilege separation enable, I get data:null as a response.  
> You can disable it afterward, and it's working fine.  
> I presume this function is there to disable a token without removing it?  
> It's enabled by default though.

no, privilege separation means that you need to configure access for the token explicitly (within the limits of the ACLs of the owning user). without, the token automatically has exactly the same access as the user itself. e.g., you could define a token that just has power management privileges for guests (for automatic starting/stopping/.. via the API), but no possibility to change the config of the guests even though the user can.

#### [Veeh](/members/veeh.47821/)

##### Well-Known Member

* [#5](/threads/api-token-config.92465/post-403378)

> no, privilege separation means that you need to configure access for the token explicitly (within the limits of the ACLs of the owning user). without, the token automatically has exactly the same access as the user itself. e.g., you could define a token that just has power management privileges for guests (for automatic starting/stopping/.. via the API), but no possibility to change the config of the guests even though the user can.

Nice that's cool indeed. Right now to solve my issue I don't use it, but I have the permission set up at the user level.  
I'll check this out, might be better to restrict the access at that level instead.  
Thanks Fabian

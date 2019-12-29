import praw
import re
import csv
import operator
import os

def process_comment(comment):
    try:
        body = comment.body
        user = comment.author.name
        linkID = comment.link_id
        id = comment.id
        parent = comment.parent()

        # !delete
        if (triggers[2] in body and isinstance(parent, commentType) and isinstance(parent.parent(), commentType)
            and parent.author.name == 'F1N1ZH_EM_ZEL' and (parent.parent().author.name == user or 'adityapstar' in user)):
                grandparentUser = parent.parent().author.name
                parentBody = parent.body
                parentLinkID = parent.link_id
                parentID = parent.id
                parent.delete()
                print('Deleted: "{}" by u/{} ({}, {})'.format(parentBody, grandparentUser, parentLinkID, parentID))
                open("comments.txt", "a").write(id + '\n')
                return

        # skip if already parsed
        with open('comments.txt', 'r') as file:
            if id in file.read().splitlines():
                return

        # keep track of number of times each user has called the bot
        if user in users:
            users[user] += 1
        elif user != 'adityapstar':
            users[user] = 1
        with open('users.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerows(users.items())
        sortedUsers = sorted(users.items(), key=operator.itemgetter(1), reverse=True)
        nathans = 'u/ | bruh moments\n---|---\n🏆'
        for username, val in sortedUsers:
            if val > 1:
                nathans += username.replace('_','\_') + ' | ' + str(val) + '\n'
        if submission.selftext+'\n' != nathans:
            submission.edit(nathans)

        # determine which trigger
        indexOfOriginal = body.find(triggers[0])
        indexOfPlus = body.find(triggers[1])
        if indexOfPlus == -1 or ((indexOfOriginal < indexOfPlus) and indexOfPlus != -1 and indexOfOriginal != -1):
            trigger = triggers[0]
            message = body[indexOfOriginal + 6:]
        else:
            trigger = triggers[1]
            message = body[indexOfPlus + 6:]

        # remove whitespace characters
        message = removeNPC(message)

        # remove leading spaces
        pos = 0
        for c in message:
            if c == ' ':
                pos += 1
            else:
                break
        message = message[pos:]

        # act on parent if comment is blank
        if not message:
            if (isinstance(parent, commentType)):
                message = parent.body
            else:
                message = parent.title

        # apply filters to parent
        message = removeNPC(message)

        # discourage repeated calls
        if (message == "[HTTPZ://1.1MGUR.COM/CDTL4VX.G1F](https://i.imgur.com/cDTl4Vx.gif)"):
            print("replied to kanye.gif")
            comment.reply("[HTTPZ://1.1MGUR.COM/CDTL4VX.G1F](https://i.imgur.com/cDTl4Vx.gif)")
            open("comments.txt", "a").write(id + '\n')
            return

        final = tabooify(message, trigger)
        if len(final) > 9999:
            print("u/{}'s comment was too long ({}, {}, {})".format(user, linkID, id, str(len(final))))
            comment.reply("[HTTPZ://1.1MGUR.COM/CDTL4VX.G1F](https://i.imgur.com/cDTl4Vx.gif)")
            open("comments.txt", "a").write(id + '\n')
            return

        # success
        print('Replying to: "{}" by u/{} ({}, {})'.format(body, user, linkID, id))
        comment.reply(final)
        with open('comments.txt', 'a') as file:
            file.write(id + '\n')
    except Exception as e:
        print("process_comment(): exception occurred")
        print(e)
        print('Tried replying to: "{}" by u/{} ({}, {})'.format(body, user, linkID, id))
        open("comments.txt", "a").write(id + '\n')
        return

def removeNPC(string):
    return re.compile("&#x200b;", re.IGNORECASE).sub("", string).replace("&nbsp;", "")

def applySwaps(swaps, message):
    final = message
    for swap in swaps:
        final = final.replace(swap, swaps[swap])
    return final

def tabooify(original, trigger):
    original = original.upper()
    if (trigger == triggers[0]):
        swaps = {'B':'13','S':'Z','I':'1','#':'','13LACK METAL TERROR1ZT':'13 M T'}
    else:
        swaps = {'B':'13','S':'Z','I':'1','E':'3','O':'0','A':'4','T':'7','U':'V','#':''}
    links = re.findall('\[.*?\]\((.*?)\)', original)
    swaps.update({applySwaps(swaps, link):link for link in links})
    final = original + " | " + applySwaps(swaps, original)
    return final

if __name__ == '__main__':
    triggers = ['!taboo', '+taboo', '!delete']
    commentType = praw.models.reddit.comment.Comment
    with open('users.csv','r') as f:
        reader = csv.reader(f)
        users = {rows[0]:int(rows[1]) for rows in reader}
    print("logging in...")
    reddit = praw.Reddit(user_agent=os.environ.get('USER_AGENT'), 
                             client_id=os.environ.get('CLIENT_ID'), client_secret=os.environ.get('CLIENT_SECRET'), 
                             username=os.environ.get('USER_NAME'), password=os.environ.get('PASSWORD'))
    print("listening...")
    subreddit = reddit.subreddit('test')#'hiphopcirclejerk+denzelcurry+test+freebies')
    submission = reddit.submission(id='cfg95e')
    for comment in subreddit.stream.comments():
        if re.search("[!+]taboo", comment.body) or '!delete' in comment.body:
            process_comment(comment)

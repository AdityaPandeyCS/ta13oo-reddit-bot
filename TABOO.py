import praw
import re
import operator
import redis
import os
from prawcore.exceptions import NotFound

def main(): # todo: refactor main()/login/exception code
    try:
        print("logging in...")
        reddit = praw.Reddit(user_agent=os.environ.get('USER_AGENT'), 
                             client_id=os.environ.get('CLIENT_ID'), client_secret=os.environ.get('CLIENT_SECRET'), 
                             username=os.environ.get('USER_NAME'), password=os.environ.get('PASSWORD'))
        print("listening...")
        post = reddit.submission('aaaaaaaaaaa')
        print(post.link_flair_text)
        # subreddit = reddit.subreddit('hiphopcirclejerk+denzelcurry+test+freebies')
        # global leaderboard
        # leaderboard = reddit.submission(id='cfg95e')
        # for comment in subreddit.stream.comments():
        #     if comment.author and comment.author.name == 'cysvendson':
        #           reddit.redditor(owner).message('sticker', comment.permalink)
        #           print("PM'ed")
        #           continue
        #     if re.search("[!+]taboo", comment.body) or '!delete' in comment.body:
        #         process_comment(comment)
    except NotFound as e:
        print("main(): exception occurred")
        print(e)
        print(type(e))
        # main()

def process_comment(comment):
    try:
        body = comment.body
        user = comment.author.name
        linkID = comment.link_id
        cid = comment.id
        parent = comment.parent()

        if history.exists(cid) or user == 'nathancountbot':
            print(cid, 'already parsed')
            return

        # !delete
        if (triggers[2] in body and isinstance(parent, commentType) and isinstance(parent.parent(), commentType) and parent.author.name == 'F1N1ZH_EM_ZEL' and (parent.parent().author.name == user or owner in user)):
                grandparentUser = parent.parent().author.name
                parentBody = parent.body
                parentLinkID = parent.link_id
                parentID = parent.id
                parent.delete()
                print('Deleted: "{}" by u/{} ({}, {})'.format(parentBody, grandparentUser, parentLinkID, parentID))
                history.set(cid, user)
                return

        # keep track of number of times each user has called the bot
        if user != owner:
            points.incr(user)
            if user in users:
                users[user] += 1
            else:
                users[user] = 1
        sortedUsers = sorted(users.items(), key=operator.itemgetter(1), reverse=True)
        nathans = 'u/ | bruh moments\n---|---\n🏆'
        for username, val in sortedUsers:
            if val > 1:
                nathans += username.replace('_','\_') + ' | ' + str(val) + '\n'
        if leaderboard.selftext + '\n' != nathans:
            leaderboard.edit(nathans)

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
        if (message == kanye):
            print("replied to kanye.gif")
            comment.reply(kanye)
            history.set(cid, user)
            return

        final = tabooify(message, trigger)
        if len(final) > 9999:
            print("u/{}'s comment was too long ({}, {}, {})".format(user, linkID, cid, len(final)))
            comment.reply(kanye)
            history.set(cid, user)
            return

        # success
        print('Replying to: "{}" by u/{} ({}, {})'.format(body, user, linkID, cid))
        comment.reply(final)
        history.set(cid, user)
    except Exception as e:
        print("process_comment(): exception occurred")
        print(e)
        print('Tried replying to: "{}" by u/{} ({}, {})'.format(body, user, linkID, cid))
        history.set(cid, user)
        return

def removeNPC(string):
    return re.compile("&#x200b;", re.IGNORECASE).sub("", string).replace("&nbsp;", "")

def applySwaps(swaps, message):
    final = message
    for swap in swaps:
        final = final.replace(swap, swaps[swap])
    return final

def tabooify(original, trigger):
    original = original.upper().replace('NIGGER','NATHAN').replace('NIGGA','NATHAN')
    if (trigger == triggers[0]):
        swaps = {'B':'13','S':'Z','I':'1','#':'','13LACK METAL TERROR1ZT':'13 M T'}
    else:
        swaps = {'B':'13','S':'Z','I':'1','E':'3','O':'0','A':'4','T':'7','U':'V','#':''}
    links = re.findall('\[.*?\]\((.*?)\)', original)
    swaps.update({applySwaps(swaps, link):link for link in links})
    final = original + " | " + applySwaps(swaps, original)
    return final

if __name__ == '__main__':
    # triggers = ['!taboo', '+taboo', '!delete']
    # owner = os.environ.get('OWNER')
    # commentType = praw.models.reddit.comment.Comment
    # kanye = '[HTTPZ://1.1MGUR.COM/CDTL4VX.G1F](https://i.imgur.com/cDTl4Vx.gif)'
    # history = redis.from_url(os.environ.get("REDIS_URL"), db=0)
    # points = redis.from_url(os.environ.get("REDIS_URL"), db=1)
    # print('loading users...')
    # users = {user.decode():int(points.get(user).decode()) for user in points.scan_iter()}
    main()
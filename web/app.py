from flask import Flask, render_template, request, redirect, url_for
import sys
import os

dataPath=os.environ["BRAWL_COACH_DATAPATH"]
backPath=os.environ["BRAWL_COACH_BACKPATH"]
frontPath=os.environ["BRAWL_COACH_FRONTPATH"]

#dataPath="/home/pi/brawlCoach/data"
#backPath="/home/pi/brawlCoach/src/python"
#frontPath="/home/pi/brawlCoach/src/web"

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, "/home/pi/brawlCoach/src/python")

from functions import *

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def homepage():
	request_method=request.method
	if request.method == "POST":
		tag = request.form["tag"]
		print(request.form)
		return redirect(url_for('tag_results', tag=tag))
	return render_template('home.html')

@app.route("/currentMeta")
def team_picker():
	battleNumber={}
	bestTeams={}
	bestSolo={}
	progress={}
	remainTime={}
	hours={}
	minutes={}
	i=0
	current_events = readCurrentEvents(dataPath+"/events/current_events.json")
	for events in current_events:
		map=events["event"]["map"]
		mode=events["event"]["mode"]
		startTime=events["startTime"].split(".")[0]
		_, _, progress[i], remainTime[i]=computeEventTime(events)
		hours[i], minutes[i], _ = convert_timedelta(remainTime[i])
		try:
			bestTeamsRaw, battleNum =readEventsStats(events, "teams")
			bestSoloRaw, battleNum =readEventsStats(events, "solo")

			bestTeamsSorted = sorted(bestTeamsRaw, key=lambda d: d['teamStats']["pickRate"], reverse=True)
			bestSoloSorted = sorted(bestSoloRaw, key=lambda d: d['soloStats']["pickRate"], reverse=True)
			
			bestTeams[i]=bestTeamsSorted
			bestSolo[i]=bestSoloSorted

			battleNumber[i]=battleNum
		except:
			try:
				bestSoloRaw, battleNum =readEventsStats(events, "solo")
				bestSoloSorted = sorted(bestSoloRaw, key=lambda d: d['soloStats']["pickRate"], reverse=True)
				bestSolo[i]=bestSoloSorted
				battleNumber[i]=battleNum
			except:
				battleNumber[i]=0
				bestTeams[i]="N/A"
		i=i+1			
	return render_template('currentMeta.html', current_events=current_events, len=len(current_events), battleNumber=battleNumber, bestTeams=bestTeams, bestSolo=bestSolo, eventProgress=progress, hours=hours, minutes=minutes)

@app.route("/currentMeta/<string:events>")
def mode_map(events):
	current_events = readCurrentEvents(dataPath+"/events/current_events.json")
	current_event=current_events[int(events)]
	try:
		bestTeamsRaw, battleNum =readEventsStats(current_event, "teams")
		bestTeamsSorted = sorted(bestTeamsRaw, key=lambda d: d['teamStats']["pickRate"], reverse=True)
		if len(bestTeamsSorted)>50:
			lenTeams=50
		else:
			lenTeams=len(bestTeamsSorted)
	except:
		bestTeamsSorted="None"
		lenTeams=0
	
	bestSoloRaw, battleNum =readEventsStats(current_event, "solo")
	bestSoloSorted = sorted(bestSoloRaw, key=lambda d: d['soloStats']["pickRate"], reverse=True)
	lenSolo=len(bestSoloSorted)

	return render_template('currentMetaDetails.html', bestTeams=bestTeamsSorted, bestSolo=bestSoloSorted, lenTeams=lenTeams, lenSolo=lenSolo, mode=current_event["event"]["mode"], map=current_event["event"]["map"])


@app.route("/processTime.log")
def processTime():
	try:
		with open(logPath+path_separator+"timeLog.txt") as fp:
			timeLog = json.load(fp)
	except:
		timeLog=[]
	return {"items": timeLog}


if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000)

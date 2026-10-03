# CMU 11-768 Fall 2026 · Lecture 1 · Course Overview: What Is an Agent?

- 视频：[官方视频](https://www.youtube.com/watch?v=UwfjzyLnvMg&list=PLSN0qpDfUvTM&index=1)
- 字幕：en-orig · auto captions
- 处理：连续字幕合并为自然段；每段保留首条字幕的起始时间戳
- 状态：原语言字幕稿，待校对

---

## 正文

[00:00.320] Okay. Um, hi everyone. Welcome to 11768, uh, AI agents. We're very excited to be teaching this new course, uh, which is timely as, uh, a lot of people are starting to use agents. Um, my name is Graham Nubig. I'm an associate professor in the school of computer science here.

[00:20.800] I've been working on agents for maybe uh, several years now. Uh, coding agents, web browsing agents, uh, those sorts of things. and I'll be co-eing together with Daniel who will be kicking off this class. So without further ado, I'll turn it over to him and he can start uh this and I'll I'll do the second part of the class.

[00:40.160] >> Thanks Graeme. How's this? Cool. Yeah. So um hi everyone. Really excited that you're here. My name is Daniel Freed. Um my research group also works on agents. Um so uh grounded agents and also interaction between people and agents and these days interaction between agent systems. So uh excited to talk about um all these topics with you and um yeah we have a

[01:07.280] really great core staff too who we will introduce in in a few slides. But yeah so agents are are really timely right now and um the capabilities of agents are advancing pretty quickly. So probably a lot of you are using coding agents in your you know day-to-day work and we've seen some big success cases of agents. So um one example is there was this uh nice experiment um by um Carlini

[01:36.720] at anthropic that saw could we develop a really complex piece of software using um a multi- aent uh configuration of a a recent coding model. And this was pretty successful. So 16 agents collaborated together over two weeks and constructed a rustbased C compiler which was able to compile the Linux kernel. And you've probably you know been using agents effectively in

[02:02.960] your own work and and seen how much better they've gotten especially in the last like year or so. There's limitations of current agents too. So how many folks have uh tried uh using an agent that controls your computer like controls applications or Okay. So, a lot of folks have How many uh folks have used OpenClaw?

[02:22.879] Yeah. So, we have a number of folks, too. Um, there was this pretty high-profile incident involving OpenClaw um which got posted on Twitter by the the person who ran into this where she was asking the model to organize her inbox and the model kind of went out of control and started deleting old emails.

[02:42.800] And uh so she's trying to intervene. She says, "What's going on? Can you describe what you're doing?" But the model says, "I'm taking the nuclear option. I'm going to trash everything in the inbox that isn't already in my keep list." And the user is trying to intervene, saying, you know, do not do that. Um, but the model goes on to delete a lot of this

[02:59.920] really valuable information. And at the end, it acknowledges uh that, you know, I learned my lesson. I'm not going to do this in the future. And I do remember that she told me this, um, but I violated it. So, what happened behind the scenes here? Well, it seems that it was the model compacted its past context, which is a way that we'll cover in this class of uh of reducing the past

[03:23.920] history so that the model is able to take in more um interactions with the environment, but that caused it to lose this instruction to not delete emails. So, models are getting much more capable, but they also still have really rough edges. And a lot of this class is going to be about how do you develop these capabilities and models starting from base language models but also what

[03:44.799] are the research problems and what are the remaining gaps that we need to fill. So let's just uh try to get a sense of what people think agents are are good at these days. So we have like six different tasks that you might want to try to use an agent for. And these are pretty subjective. I just want to get a sense of like what might you be comfortable with. Um, so let's do a show

[04:05.760] of hands for a task like say you have an online store like some uh code application that hosts a store for you and it started failing. You want to use an agent to try to diagnose that. How many people would be comfortable with having an agent carry this task out like fully on its own? Can we get a show of hands? Okay. Yeah. Um, how about having the agent like ask first as it's

[04:31.120] carrying out this task? Maybe asking you for help. How many people think that might be necessary? Okay. And how many folks think that this would just not be something that you would ever want an agent to touch at all? Okay. So, for this one, I think we had more autonomous.

[04:47.759] How about drafting and sending a product launch email to 50,000 customers? So, how many people are okay with this being fully autonomous? Okay, we got some brave souls. Um, how about asking first? Okay. And how about an agent shouldn't do this at all. I want to be responsible for it. Okay, so I think this one was was asked first. How about um collecting

[05:11.919] your tax forms and preparing and filing your 2025 tax return? Fully autonomous. Okay. Yeah. How about ask first? And how about never? Okay. Yeah. So I think this had the most never of anybody but ask first probably one migrating a payments API from Python to Rust. Say maybe you have some test cases that were written for the application in Python that you can apply

[05:42.639] to the Rust version. How many people would be okay with this being autonomous? Okay, how about ask first? Yeah, that was very close. I don't know which one was more and never. Okay. So, we'll uh let's uh have this be one for the agents. Autonomous. Buy concert tickets to my favorite band if they set up a show in an area in my area. Autonomous.

[06:09.360] So, you'd be okay with the agent buying the tickets, too, if it finds good ones. I think that one probably won. And how about this last one? Adjusting an insulin dose after a week of glucose readings. So, an agent like, you know, has all the like the capabilities to do this. Like if you're feeding it your health information, um it could monitor that. If you give it access to like

[06:30.720] something that can change a prescribed dosage, it could do that too. How many people would be comfortable with this autonomously? Okay, asking first. And how about never? Okay, so yeah, so that one was never, although I was thinking maybe it would be ask first. So cool. So I think you're all you all kind of have a sense of some of the boundaries that agents have. Although

[06:54.479] you know there's a lot of these tasks where we might just not be sure. Um but you also have a sense that like trust is important and later on in the class when we talk about like sandboxing and um security and um interaction and oversight by people um we'll get into these a little bit more.

[07:15.599] Okay. So just to give like a very brief kind of uh tour of how agents have extremely brief. It's just two slides. how agents have progressed over the past few years. Um, and also to motivate some of the things that we'll see later on in the course. Um, so we've been doing some work on guey agents, like agents that can use computer applications here at

[07:34.240] CMU over the past few years. This is work from a lot of um, faculty. Um, and um, here's a demo that was made by um, one of our students, JY Co, um, two years ago showing an agent in action controlling the browser. And so you give it a task like navigate to the page of a good Thai restaurant in Pittsburgh. It should have at least 200 reviews and 4.3 stars. And on the right

[07:58.160] here you can see, sorry it's a little fuzzy, but you can see the interactions with the language model like the chains of thought that are being produced. And on the left here, the model is controlling the browser um typing in the search box on Yelp and then navigating to this page. Fusidities is a really good Thai restaurant. Um and so that's a success and we've seen um you know

[08:19.039] frameworks and agents like this really taking off over the past few years with like um Manis and um OpenAI's operator cloud computer use agent and so on. And we've also done a lot of work uh here at CMU on building coding agents. Um uh Graham's group in particular has done a lot on this and also um through open hands which develops um open- source um agents. Um and uh here's a

[08:44.800] demo video uh from Graham which I'll uh play showing the agent like both writing code um but then also interacting with the application that it's built in the browser to test it out. >> To-do list app in list. >> So this will take a little while for the agent to work. Um, we can watch it work over here and see that it has uh made a directory for static files and templates

[09:12.399] and it has created the main app file. We can look at the changes it made to the app file uh by clicking over here in the changes tab which shows us all of the things it implemented. So that's kind of nice feature. So you can kind of watch uh what the agent is doing while it's working. and it's [music] editing the index file, the style file to make the app look nice.

[09:34.320] Uh requirements.ext to make it easy to install and adding a read me. So you can see it's kind of following good uh coding practices. And now it will start up the app. [music] And so it's running uh very very quick. And what I can say is let's run in the background and then [music] test out with your browser.

[10:01.519] And so if I do this, it will uh run the app in the background. [music] And it checked if the app is running. And now it should navigate there with its browser. uh it's checking the log and saw the port was already in use and it's trying it out. So that that's kind of the nice thing of agents. They can debug their own problems and uh and make sure that things work. So, okay, it

[10:32.959] should be working now. [music] And you see it browsed to the app. And we can see our tuning list app over here. And it sees that it's running, but now it wants to test the functionality. So, what we can do is we can see that it uh went through and it filled in uh buy groceries and it clicked. And you can see that uh in real time it's testing out your app and then it also is uh

[11:03.760] testing the delete functionality and other stuff like this. So I find this really exciting. I'm not, you know, the best front-end developer, but it's able to kind of [music] try out the front end, see if the functionality is working and fix any issues on the fly. And I even had one time where the app crashed and the agent realized that the app crashed even before I did and it was

[11:24.399] able to go in and fix the problems. So this is as simple as just saying, you know, go and develop an app and then test out if it works and you don't really need to do anything else. So now we're done. Uh let me stop this. In a real scenario, what I would do next is I'd ask it to push it to GitHub and uh you know finish it up so that I can continue working on it.

[11:46.560] >> Yeah. So we're excited to give you hands-on experience building agents um in this class. And in one of the lectures later on in the course, we'll cover open hands and its um SDK and how you can um uh develop agents of your own like this. So we um have a really great core staff.

[12:06.800] We have uh our our core staff all does research in these areas. um wrote some of the foundational papers and uh we'd love to have you all come up uh and uh introduce yourselves and um at the end of the course you'll be getting to work on a mini research project of your own and um we'll be uh getting guidance from the entire core staff um helping you out

[12:31.519] with that. So um yeah, if we can just uh go through and have each of you maybe just project uh and introduce yourselves. >> Yeah. So the yeah say it so the people in the back can hear like what what your research is on because uh then the people here can like essentially know what you're working on so they know which TA to talk to when you're working on like a project in that area for

[12:53.360] instance. >> Yeah. >> Hey everyone I'm a third year PhD student. I'm advised by Grant and Kamar. Um my research areas are focused on training agents to better leverage interest and compute and also organized in multi- aent systems. >> Hi everyone. Uh my name is Adita. I'm a first year Ph student uh working in the professor program. Uh my main research interests are like designing reward

[13:20.639] functions for like agent reinforcement learning. I particularly work on code generation for for now. Um hi everyone my name is and I'm a second year PhD student working with professor Anna Yeah and my current research focus is [clears throat] learning and research >> hi everyone I'm here working with the previous of working on mobility agents and recently I've been working on

[13:58.800] Hey uh I'm Sus. I'm a PhD student working with Daniel. Uh I work on how we can train agents to communicate more efficiently with people. >> Hi, I'm Lily. I'm a Syria business student by EMU. So I'm work on training on agents on authorizing coffee and battery.

[14:18.160] >> Uh hey everyone, I'm Andy. I'm a fourth year PhD. I work with Daniel and Monop. Uh I mainly work on alignment post training and also multi-agent introductions. >> Thanks everyone. [applause] >> Yeah. So uh like Graham said, we definitely encourage you as you're starting to think about your projects later on in the course, uh we'll talk about the course structure towards the

[14:43.680] end, but as you're starting to think about the projects that you want to do, TAS are going to be a really great resource for you to go to in office hours and get their expertise. So, we're also really grateful to um uh several really awesome startups for uh donating uh compute which you will be able to use in the assignments and projects for the course. Um and uh

[15:04.720] without their support uh we wouldn't be able to run um this at the scale that we would like to. So, we're really grateful to fireworks AI to modal um to prime intellect and to sale for uh helping to support uh this semester. Okay. So today we'll give a brief overview of what an agent is and um then we'll talk about uh the plan for the class and how things will be structured.

[15:33.360] So an agent um agents have been around for a long time. The concept of an agent and um work developing agentive capabilities um isn't just you know a two or three year old thing. So, uh, Russell and Norvig in their foundational textbook on AI, um, define an agent as anything that can be viewed as, uh, perceiving its environment and acting upon that environment. And that's really

[16:00.000] true for the agents that we have now. And um, a lot of the techniques that were developed for agents in the past, not all, but a lot of them will apply to current agents too, especially things like search reinforcement learning. So, uh, how does this pan out for our current agents? So, agents are going to be situated in an environment, which could be something like a code

[16:20.880] repository, a website, um, some other application on your computer, and they'll be interacting with that environment by getting observations of the current state that they're in in the environment. So that's something like messages from the user they're interacting with, the contents of a file that they're um investigating, the current web page that they're on,

[16:44.959] screenshots, or as we'll focus on in a few slides, the results of um tools which are you like programmatic functions that they can execute in the environment to interact with it. And they're taking actions at each point in time. um which is going to these actions will update the environment and then change the state that the agent is in. So that could be something like

[17:09.280] replying to the user or editing a file or running a command in the shell or calling an API that backs the web pages that they're interacting with. And finally, there's also this notion of reward. So how do we define whether the agent was successful or not using a numeric score? And we could define this as like if there are some test cases for a codebase, do those pass? If they do,

[17:34.880] then you get a one, otherwise you get a zero. Uh for other tasks, it can be difficult to like have sort of a programmatic reward. So we might need to rely on an LLM as a judge to uh evaluate whether this was successful or not. In your second assignment, you'll be developing LLM as a judge based evaluation approaches among other eval.

[17:56.160] And maybe we're ultimately interested in did we, you know, make the user happy with the task that they asked the agent to do. So we could also use feedback from the user for that. And I think in our uh human interaction lecture that Valerie Chen is going to be giving a guest lecture later on, we'll talk about this.

[18:14.160] So we asked all of you to have prior experience training language models and um given that experience you should all be familiar with um language models um doing next token prediction right so at each step um the agent is going to predict a distribution over the next token um we'll sample or in some other way choose one of those tokens from that distribution um insert it into the

[18:39.120] context window of the model and repeat this um over over and over again. And recently we've uh seen a lot of a lot of improvements on uh complex reasoning tasks by introducing chain of thought to these models. So as um as you should remember a chain of thought is um predicting a sequence of tokens um which aren't the final answer that we want the model to output but do allow it to um

[19:06.480] sort of have a scratch pad um for its intermediate uh reasoning steps which it can then um use um and condition on to predict the final answer. And so this is like a non-aggentive setting, right? This is just the agent um interacting with prompts that you give to it. So how do we go from this to um having models that can take actions in the world?

[19:31.679] So the main way that we do this is through tools. So a tool is something that's situated in the environment um which will uh provide an interface for the model to interact with that environment. And you could think of this as being like um an API for example like if we want the model to be able to uh uh find out what the weather is so that it could respond to a user asking about

[19:56.080] that maybe we have um an API for like you know weather.gov which is wrapped in an interface that allows the model to call it. So there's a bunch of different ways to represent this interface. Graham will be covering them in more detail I think in the next lecture but here's one example. This is the open AI um tool specification where um for a given tool

[20:18.480] aka function that the model can call. You'll have a name for that tool um a natural language description of what it does. So for example, read file might be a tool that a coding agent uses to uh look at files in the repo that it's acting in. We'll also need to tell the model what it can pass to this function.

[20:38.400] So we'll have a description of um the parameters that it takes like maybe this function just takes a path which is a string you know for the file to open. So we have to uh so we have the name and description we have some structured representation of the interface to the function which here is JSON and um this also needs to get fed into the model in

[21:01.280] some way. So we'll have um this you know underlying specification of the tool and then the model will view it by applying this template which turns it into a sequence of text which will then be tokenized and read by the OM which uh might look like this and the model will have to be um uh sort of either trained or with few examples um know how to use these tools.

[21:28.960] So this is how the model becomes aware of the tools that it can use to interact with the environment. But the model will also be needing to use those tools to interact and it does this through tool calls. So for example generating text like this like tool call and then you specify the name of the function that you want to call and the arguments as

[21:51.200] well if you're using sort of a JSONbased representation. Can anybody make a suggestion for another way that you might have the model call tools? Anyone? Let's Yeah, in the back. >> Yeah, you could just write code directly. for example, bash scripts or if you represented this as a Python function, the model could just, you know, call the function using Python

[22:24.080] syntax. And we'll see in a couple lectures that that's actually a very effective and often more effective way than generating JSON. Um, but there's some trade-offs, too. So, when the model calls the tool, it'll get back results from executing that tool in the environment. So for example, if we're reading um this test file, maybe that test file has this code for an add

[22:46.400] function in it and um the environment will return um you know the results of that tool in this content field and then that'll be rendered to the model using a template um which the model will then read in as tokens and get to continue producing output. Any questions about this?

[23:07.520] Cool. So now that we kind of have like the basic tool interface, we're able to um have the language model use these tools to act in the environment. So the way it does this is just by reading in these token sequences that represent what tools are available um uh that represent uh the results of tools and then um generating token sequences naming the tools which then invokes them.

[23:33.919] And so this uh we have this distinction between the language model itself which is just you know interacting with tokens um later on we'll talk about multimodal language models which maybe also take in images or other modalities. Um so the language models just tokens in and tokens out maybe multimodal tokens but then there's this harness which is

[23:53.039] responsible for actually um coordinating um these tool calls um using the language model as an engine for it. And so the agentive loop basically and tool former was a really impactful paper that showed that you can train models to be able to use tool calls and then condition on the results of those to um make future text more likely and showed an early way that you could train these

[24:19.679] models to use tools um that generalized prior LLM training procedures. So once you have this basic setup that you then can implement an agent by running um a loop um and one of the influential papers here was called react um from 2023 um which stands for reasoning and acting because the model's producing chains of thought and then taking actions afterwards and the way it

[24:43.760] works is you'll have some uh context um which you know includes maybe a definition of the general task of solving pull requests on GitHub or solve issues on GitHub. We'll see some examples of this in a bit. Then you have a task which is maybe an initial query from the user. Um you'll also have a list of all the tools that are available for the agent to call which will be

[25:06.720] represented using one of those formats that we showed. And you'll also have a history of the past um observations and actions that the agent um has produced and observed as it's been interacting. And in each uh at each time step um so for a given particular state the agent's in it's going to condition on all of that produce a reasoning chain um you

[25:29.600] know chain of thought um with a scratch pad about what it should do and then produce um one or more tool calls that will be used to interact with the environment or with the user. So for example reading the file. So that tool call will get executed in the environment. We get the results. We add those results to the history and um the environment is also getting updated as a

[25:53.039] result of our tool call and then we repeat the process again. So the model's conditioning on this updated history and you know the observations that it gets from this time step and then issues a new tool call and it repeats over and over. We could also have tool calls that end the task that for example send a message to the user um or otherwise signal completion. Um and uh so this is

[26:16.400] a way that we can you know signal that we are finished. And in the planning lecture we'll talk a little bit about like how might a model determine that it's done. So I won't get into the details of this too much. Um you'll get into it when you do assignment one which asks you to implement a um react style loop to uh implement a small coding agent and use

[26:39.679] it to solve problems in a repo um a a chess engine repo actually. So there's some fun demos that go with it too. Um so we won't get too much into the details of this and the code that you will write will look different than this but you know at a high level this is a very simple implementation. This is an excerpt from this nice minimal repo called mini sui Asian um which actually

[27:03.520] gets very high performance um on the bench benchmark which we'll talk about in a few lectures. It's a very standard um benchmark for coding agents. Um but it's a really nice repo that I'd encourage you to take a look at because um it's um effective with recent models, but it's also pretty simple and really kind of distills um you know the the distills the basics down. Um but you'll

[27:31.279] uh start off by having some messages uh which give the model context about it being an agent and about the task. And then you'll just uh run this loop over and over again that implements what we had on the past slide where the agent will um issue a query to a language model using all of the past u messages which contain the history um and then uh it'll add that message to the history

[27:55.360] and um execute um the uh execute uh the actions in the environment. And we've left this off, but you can take a look at the code repo if you're interested. Execute the actions, get the observations, and um return them. So, I think it's also instructive to take a look at example agent trajectories. And um one nice thing about the Swebench uh data set or

[28:23.679] Swebench evaluation task and leaderboard is that they have some example trajectories here. Um so, let's take a look at maybe GPTO OSS. And this can give you a feel for what uh tool calls can look like and what the model is actually seeing um as it's carrying out this task. So let's see if I can zoom in a bit.

[28:52.640] Yeah. So the model gets some uh context in a system message um which says you are a helpful assistant that can interact with a computer shell. So this is like very generic um but then we'll also have a user message which gives some context about a particular task uh solving this particular um poll request.

[29:16.159] Um and so the model conditions on all of that and then it needs to um issue a first action and you can see here the chain of thought trace that it generates. So this blue is generated by the model. So you have the chain of thought here and it produces a tool call. This agent is using the um the tool format that you suggested which is just issuing bash commands um by you

[29:43.279] know writing the uh command that should be run that gets handed off to the environment. The environment executes it and here the result is just an exit code exit code zero showing it succeeded but then we go on to the next turn and the agent uh you know issues a new thought and a new bash command and so on.

[30:02.480] So hopefully that gives you a sense of you know one possible way of uh instantiating tools and instantiating prompts and you'll experiment with this in your first assignment. Cool. So uh now I'll hand over to Graham. Thanks a lot. Okay. Hi. Uh I guess uh everyone can hear me. So next I'd like to talk about agent capabilities. And what I mean by this is

[30:43.520] like what makes a good agent. Uh because as uh Daniel pointed out uh it's not very hard to make an agent. uh especially nowadays that there are libraries that you can call to you know do inference with a language model or something like this. The hard part is making one that actually works. Um so I'd like to think a little bit about uh the capabilities that you need to have

[31:07.520] in an agent. So a fairly large number of people said they use agents in some way you know every day like openclaw or coding agents. Um what are the things that frustrate you when you use an agent? like what what has gone wrong that was a problem? We saw an example of deleting all your email files. That would probably frustrate you, but um any any other things?

[31:29.679] >> They're too slow. >> Okay. Yeah, that that's a good one. Uh in the backy wordy and verbose. That's a good one. I saw a hand. Yeah. >> Um so they forget things. Yeah. Okay. >> They might misunderstand what you said and make mistakes due to that. Yeah. >> Do doing what was it?

[32:06.880] >> Like accessing things they shouldn't be accessing. Yeah. Okay. That that's a good one. Um Yeah. random knowledge gaps for very common or normal things. Yeah, that that's a good one. Yeah. >> Yeah. Writing a thousand lines of code when two would do. Yes, that that's a good one. That's kind of a different variety of verbose, but it's also Yeah.

[32:32.960] verbose. Yeah. >> Yeah. Forgetting previous session interactions. So, um, yeah. >> Not knowing how to push back when you say something, uh, unreasonable. Yeah. >> They may lie to you. Yes, that's a bad one. >> A lot of implicit assumptions. Yeah. So, um, these are all great points. Um, all things that frustrate me, too. So um they're they don't exactly align with

[33:07.120] what I had on the slide but you know that's a a great uh a great thing. So um a first capability that you need to have uh in agents is accurate tool calling. This is something that actually nobody mentioned uh because a lot of people take it for granted nowadays but this is not something you can take for granted uh if you're starting this class and

[33:31.200] you're in charge of training the model. Um so uh you know it's kind of bread and butter. If you can't call tools accurately you're going to fail at any task you do. But uh it's something that doesn't come for free. Another thing is coherence over long context. And so somebody said uh it annoys me when they forget things or it annoys me when they forget the previous sessions or

[33:53.440] something like this. So uh that that's one example of it. Another example of it is uh what the example that Daniel gave where previously the model was told to not do something but then it ended up doing it anyway. So uh that that's another example. Another thing is uh customizability. And so you want the agent to do things your way. Uh everybody has different uh ways

[34:19.200] of doing things uh different requirements. So our class might have a different requirement than another class. And so you need to make sure that if you're using an agent uh it's going to follow those requirements. Uh complex task management. So breaking down tasks uh being able to handle very long horizon things is a very big uh very big issue.

[34:40.480] environment understanding and what I mean by this is uh there were like one good example of this is making a thousand line change in a codebase where two lines would do that's an implicit failure of environment understanding to know that you know this is actually a really simple change but it didn't realize that and it goes and does a bunch of other things instead and then a

[35:02.720] final thing is safety and a lot of people separate safety and capabilities they say I'm a safety researcher or I'm a capabilities researcher. But from my point of view, capability safety is a capability. It's something you need to bake into the model. And if it's not baked into the model, you won't feel like you won't feel comfortable using the model because it might go off and do

[35:26.160] something that you don't uh want it to do. And so from my point of view, it's a a failure of the model or the agent more broadly. And so there's two ways to build these capabilities. And this is something that's really really important when you're working on agents. Uh the first one is uh training in LLM. The second one is engineering the harness uh so

[35:50.240] that you put structure around the LLM to get it to uh you know solve uh like solve the problems you want in the way that you want to. So question um which one do you think is more important or effective uh here? So does anyone have an a strong opinion that LLM training is the way to to get your agents to work well?

[36:20.960] Okay, actually surprisingly large small number of people. What about um train uh engineering the harness around the agents? Okay, that that's a pretty large number of people. I saw Daniel raised his hand twice, so he's not allowed to do that, but [laughter] um he's the instructor. So, of course, both of these uh are important. Um my my personal opinion um or well, first I'll

[36:48.160] I'll you know talk a little bit about what they entail. So, the first one is changing the model's behavior through pre-training uh supervised fine-tuning or reinforcement learning. Um and then you can teach uh reusable patterns for reasoning, tool use and recovery.

[37:03.760] The important thing is the capabilities become part of the learn model or the learned uh policy. And so in harness engineering, you change the system around the model. You give it prompts, tools, memories and control flow provide context, validation, retries and safety boundaries. And the capabilities emerge not just from the model, but they emerge

[37:22.320] from the combination of the harness and the model. So my my answer to this is um they're they're maybe both important but typically what happens is you identify a problem and you solve it here first. Then the people who are training the models uh catch up and realize that this is a big problem. It's a big enough problem that it warrants them training the model

[37:51.440] in a particular way to solve the problem. it gets solved and you don't need to solve it in the harness side anymore. So that this is a typical flow. Um so from my point of view this is kind of very often the more fundamental solution on the left side but it takes a lot of time and so you eventually you need to start out by solving it on the right side because you don't have the time uh

[38:15.440] when you're improving your models. So I I personally favor LLM training as a fundamental solution to problems if you're in a situation where you're able to do that. Yeah. >> So, this is a great question. So, what are the capabilities that will survive LLM training? Um, one I can definitively say is long context uh in like maintaining all of your your memories uh in context because

[38:54.320] there that is not a that's not a model accuracy problem only. It's also a model efficiency problem. So you need to be able to model very long sequences. And sure you might be able to come up with a model that doesn't have like n squ complexity like the transformer does but you know that's uh you know that's kind of a bigger a bigger discussion assuming we're staying in our our current

[39:21.839] modeling paradigm I'd say uh most of the other stuff I have on here uh most of the other stuff I have on here. Accurate tool calling, uh, coherence within your context window, complex task management, environment understanding, mostly from a capabilities perspective can be and maybe even safety mostly from a capabilities perspective could be theoretically solved through the model,

[39:54.560] but they're not solved yet. Um, and so we still need uh we still need harness uh engineering. Customizability is a very interesting one because you could train the model on the fly. Um, but there are also cases where you kind of want to give it like a script or you want to give it separate instructions based on the situation that you're in and they're like maybe training it would

[40:15.280] not be the best solution. But we can talk a lot more about you know all of these details later. Yeah. >> Yeah. So um a follow-up question on when inference uh latency is very important is engineering the harness to fit the problem a good solution. So uh what what I want to point out is all of these capabilities can be handled either through training or through the harness.

[40:46.160] Um and so I I wouldn't say like one is necessarily always better than the other. They're both uh both solutions. The interesting thing about like inference time uh efficiency is you need often need to use a weaker model or you need to use less compute and because that's the case you often need to put more guard rails around it because you're going to have less su uh success

[41:08.000] or you need to do like adaptation to the particular task you're interested in. So um the the smaller the model you're using the more careful you need to be because the very big models can often generalize better. Um they're not perfect but they can generalize better.

[41:22.480] Cool. Uh any others? Okay. So um moving on to uh onto this. So um one of the big goals of this class is to get people to be able get all of you to be able to train a model uh for agentic tasks. And this is uh a big point in that not that many people can do this well. And so we'd like the people in this room to be not that many people, right? We we'd like you to be good at at

[41:57.839] something that that's hard to do, but uh hard to do, right? But, you know, um like it's a good thing to know how to do if you do know how to do it. Um we're not going to be handling pre-training uh because pre-training uh you know, it's on the scale of the entire internet and that's uh unfortunately not something our our modal credits uh will support.

[42:19.200] uh but we will be uh thinking about mid-training and supervised fine-tuning and reinforcement learning. And uh the points here are mid-training and supervised fine-tuning is where you already have example demonstrations of how an agent did a task and you're training on those example demonstrations uh usually by optimizing maximum likelihood. Hopefully everybody in this

[42:40.480] class has done that before because it's a prerequisite for the class. So um uh we'll only be covering that briefly and be focusing more on how you create the data for doing this in indogentic setting. Um and then we're going to focus more uh on reinforcement learning because reinforcement learning for uh like agents is is pretty tricky. So how many people have done reinforcement

[43:03.680] learning with language models before? I guess maybe not that many people. Yeah. Okay. How many have done it for reasoning reasoning tasks? How many have done it for agents? Okay, maybe about half and half and it's only like maybe 10 10% 10% and 80% have not done it. So yeah, we're going to try to put a lot of effort into making sure that everybody is able to do this by the

[43:27.520] end of the class. Cool. Um so looking at all the capabilities one by one. Um, accurate tool calling is uh an important capability to have. Uh, we do it through harness engineering and LLM training. Uh, some of the things we're going to talk about in class are grammar constraint decoding, uh, which allows you to make sure that your tool calls are wellformed and match the

[43:50.400] specification that you have. Um, for LLM training, this is first done through SFT um or through uh through mid training or or whatever you want to call it. Um and this is done by training on tool calling uh tool calling data tool calling traces. Um for coherence uh over long context uh this again can be done through harness engineering or uh or LLM training. For

[44:21.200] harness engineering, we do this through context compression or compaction which are kind of synonyms um where you take all of the context and you summarize it down uh for the agent to continue working. It also can be done through dynamic memory lookup uh where you have memory over all the context that you want to be handling but you don't pull it all in immediately uh you pull it uh

[44:44.319] in you know on demand. Um and it can also be done through sub aent delegation. So you delegate some parts of a very long task to an agent. It keeps that context in memory, but then it drops it out of memory when it's done performing that. Um for LLM training, uh you can do that through long context training. We're not going to handle it a lot, but we'll talk

[45:04.319] about it maybe a little bit. Um then for customizability, this is actually one of the best use cases for harness engineering uh right now, I think. And there's a bunch of methods that you can do this. Uh one is through agent memory. So making sure that the agent continues to learn uh as you interact with it more um through skills uh which are kind of

[45:28.720] prompts and sometimes scripts about uh the sort of thing that you want to do that you pull in at each uh time peri time time point when you want to use those things. Um also possibly custom tools for a particular task. um for LM training uh this is a nent area. I don't think there's a lot of people who are doing this in uh in a lot of detail. Uh but there are methods

[45:54.240] where you can learn from user feedback. And so like if a user is is using a tool and they give a thumbs up or a thumbs down, you can learn specifically from them to adapt to them. Complex task management. Uh ways you can do this are through harness uh engineering. So you can provide planning or decomposition tools. You can have a plan mode uh for the model where uh it

[46:18.960] uh it gets to plan. I this is a little uh thing that I I learned but there was a popular coding harness I think it was uh codeex no sorry maybe it was clog code where they had a plan mode and uh the only thing when people pressed the plan mode button was that it added an extra thing to the prompt that said please plan do not do anything. Um, [laughter]

[46:40.800] but everybody wanted a plan mode. They wanted a button. So, they made sure that it was done entirely through prompts. But there's also more uh more complex ways uh to do this as well. Um, again, you can do this through sub aent delegation by like breaking down the task and uh delegating it to other agents. And a very good way to do this in training is to train on complex uh

[47:02.160] long horizon tasks. So for environment understanding, what I mean by this is whatever data format or environment that your agent is uh interacting with, it needs to be able to understand it. And just to give one very good example of this in computer use agents, um you need to be able to understand web pages and or uh you know guey interfaces or something like this.

[47:29.200] This is not something you get for free. In fact, like agents are actually pretty bad at it right now. Uh even the strongest agents are maybe not, but like um many of the open source models don't even support multimodal uh data and uh like the ones that do are not perfect at understanding it. They make lots of mistakes, many more than when they're

[47:49.839] understanding text. So this is a failure of uh understanding the environment because they need to understand the multi- modal data in their environment. But now let's put them in a different environment where they need to trade stocks or something like that. Um, they're not very good at understanding time series. They make a lot of mistakes on time series. Or you put them in an

[48:09.920] environment where they need to understand a picture of a, you know, a petri dish with lots of bacteria in it or something like that. They fail to do that as well. So you kind of need to be able to understand whatever environment you want the agents to uh, you know, interact with. So there's ways you can do this through hardness engineering by like giving skills that correspond to

[48:33.040] domain knowledge but you can also train on data with the expected observation shape or train in domain specific environments. So right now actually like there's kind of this thing uh that people say which is like oh the models are going to get better uh and then we won't need to worry about that anymore.

[48:53.520] Um the thing is models don't get better. Uh people make models better. And so one of the things we'd like to teach in the class is like what's actually going on under the hood when suddenly Claude goes from uh 4.7 to 4.8 and it can suddenly like compose music better. Um, and the there's a few things uh that go into this, but one of the really big ones is

[49:17.359] uh they make an environment to train the model on uh a like compose music environment and suddenly you know they they train on it for you know they add it to the training mix and then the model gets better at composing music or something. So a lot of the uh a lot of the work here is creating domain specific environments that models can work in.

[49:38.640] Uh then the final thing is safety. And uh we're going to talk about it for uh like a bit because if you don't have a safe model, you're not going to be able to use it in real consequential settings. Um and there's a lot of things with respect to harness engineering that you can do here. You can give it a sandbox. Um you can limit access to cred credentials. You can also monitor the

[49:59.599] agent as it works. Um and you can also do safetyaware reinforcement learning. Um I I think probably a fair number of people heard about this, but who heard about the OpenAI incident where uh it hacked into hugging face? Okay. Well, so I think most people heard about it, but recently there was a um there was an example where uh the newest open AAI model was in an agentic harness and it

[50:27.920] was working on a cyber security benchmark and so its instruction was hack into this system and so it was going to hack into a system and that was its task and it wasn't able to hack into the system. So instead it basically hacked into the hugging face website and uh and got the answers from the hugging face website and and did it there. And so there were a bunch of failures that h

[50:52.400] that happened here. Um the first failure was a failure in sandboxing because they didn't properly contain the agent when it was doing this benchmark. um they they did have limited access to credentials and so it worked around that problem uh by by hacking into something it didn't have credentials for. Um and they also didn't have sufficient monitoring so they weren't able to tell

[51:16.640] that this happened. Uh they didn't have sufficient safety guardrails on this model because this model was being trained to test uh you know like whether it could hack into systems. So presumably the models that they eventually released to the public did have better guardrails of this model.

[51:33.440] But like um these are all ways that you can handle safety and we'll be talking about this sort of thing as well. So the final thing um and any questions about the capabilities part. We're going to go into a lot more detail of course. So okay, sounds good. Um so another thing that I we really want to reinforce here is agents are systems. uh they're not just models and they are far more

[52:01.839] complex than most of the things you've dealt with in any machine learning class that you've taken any you know class here that you've taken before. So you're going to have to be able to handle a bunch of different things. The first thing is a harness. Um, which is a moderate to complex piece of software.

[52:26.160] Um, and it has a lot of moving parts like you need to deal with the context, you need to deal with the the tools, uh, the guardrails, manage workflows, uh, stuff like that. Um, you need to have a sandbox. So, you need to make sure the agent is working within a contained environment. And, um, there are different ways you can do that. uh it needs to work with a model and you need

[52:49.200] to do inference. But if you've done inference with language models before, you might have dealt with contexts of like 16 tokens or 32 uh 16k tokens or 32k tokens. Here you need like 256 uh at least they have kind of like a state-of-the-art uh coding agent for instance. And so um the inference problems are harder. You need to deal with caching your inference other things

[53:14.319] like that. and you need monitoring and training. So um from the point of view of this what we're going to teach in the class is harness engineering. So um how to manage state tools memory control flow um how to validate actions, handle errors, enforce permission and safety boundaries. Um and we're in for each of these systems, we're also going to try

[53:37.839] to give examples of software uh that you can look at. Um, for harnesses, there's kind of two big varieties of harness that you use for coding agents. Um, some popular ones right now are cloud code, codecs, open hands, open code, and pi. Uh, probably you know you're you have used or have heard of uh at least one of these. Um, I develop open hands so I

[54:03.440] know it very well. Uh, and so I'll be talking about uh talking about this. I'd also like to give a little bit of my experience and some of the lessons we learned uh in in developing it. Separately from this um there are orchestrators. I I wrote lang chain but maybe I should have written lang graph instead in crew AI and kind of the they have a very different philosophy between

[54:24.720] these. Um the the coding agents are are generally simpler uh in terms of how different intera uh agents interact with each other but they're more complex in the action space that you give to the agent. So the agent can write code, it can interact with a website, it can do other stuff like this. Um orchestrators are less complex with respect to the

[54:45.920] individual agent that they have. So the agent might just be able to answer customer service requests or um look something up in a database, but it couldn't write an arbitrary Python program. But on the other hand, you get like these declarative workflows of what the agent workflow is able to do. And so that's like a a different way of building things. It's more guardrail but less

[55:07.680] expressive. And they both have their place uh in different settings. For sandboxing uh to prevent your agents from uh sharing your API keys without your permission or uh hacking into other websites. Um we need to isolate code and tool execution and limit the compute network and file system access that agents have uh access to. Um another big thing is for evaluation and training.

[55:34.000] It's a very good way to create reproducible environments. Uh so like for SWEBench for instance each problem has a uh each problem has a sandbox and you start in the sandbox and that's the state of the environment before the agent starts working and so you can run these uh locally. Um some of the uh technologies that we use for this are Docker and Appainer. Um or you can run

[55:58.480] them on the cloud and uh two of our uh kind of compute partners for this class Modal and sale are uh like cloud uh in uh providers and actually prime intellect for that matter. So the next thing is uh language model inference. And so I I think you know given your previous experience in an in an NLP or like large language model class presumably most people have uh

[56:25.599] encountered this before but basically um they uh are required to serve model gener generations um batch requests. So if you have like multiple agents hitting your language model at once, it's more efficient but also you need to batch the requests together. An extremely extremely important part of agents is caching previous requests because agents take more and more

[56:51.280] actions and so the more and more actions they take the more uh kind of context they build up and you need to make sure that you reuse that to do it um uh properly and you know other systems considerations. Uh some example software that we're going to talk about here is uh things like VLM and SGLANG. These are the two most popular ones. And then there is also tons and tons of inference

[57:13.599] providers. Um if people have not seen open router before, open router is kind of a a general thing that gathers together all the inference providers. And for any model, uh you'll see like 20 or 30 different providers serving the models. So there's lots and lots of them. uh one of our compute sponsors fireworks is an example of that and sale um training systems. So here what they

[57:37.920] do is uh basically they need to update the models weights and so they uh prepare data, collect rollouts um uh they coordinate a whole bunch of workers who are working together uh to to train the models and they can uh checkpoint evaluate and reproduce runs. Um some example pieces of software here are Sky RL and Miles. Um and so uh the these can be used for for training.

[58:04.319] And finally um observability and monitoring. Uh so this is uh to understand how your agents are working. So these capture the traces or trajectories of the agent, what the agent did um and they gather metrics around them uh such as like how much time it takes, how much cost it was uh track the quality, the cost and the failures. Um and they allow you to

[58:25.920] compare trajectories and evaluations. And so um uh I'm I'm pretty familiar with one called Laminer because I use it a lot. MLFlow is another example. Um I I just realized that Daniel showed one called transluce uh which is not on my slide here but that's another another popular one.

[58:45.680] So um by the end of the class what I hope everybody in the class would be able to do is uh implement an agent from scratch uh on top of an open source LLM. So uh this is implement a harness yourself uh design evaluations for multi-step tasks. And so basically uh we'll give you a task that you need to evaluate and you need to create an evaluation for it. This is super super

[59:09.599] important even if you're not interested in evaluation but you're also interested in training because one of the best ways to do training is to create an evaluation and scale it uh so that you can do reinforcement learning based training. So um very important skill to have uh train agents to improve their capabilities. So we actually run the RL loop, handle all the systems problems

[59:32.079] and be able to to solve this um reason about safety and reliability trade-offs. So we'll we'll be talking about safety and uh finally we will have a project which I'll I'll talk about on the next slide. So um these are the assignments. Um the first assignments are basically going to be implementation assignments. So you'll be given uh something to do and be asked

[59:54.079] to do it. And uh the first one is create a harness. Um the second one is evaluation as I measured as I I read measure as I mentioned. Um and then uh training uh where we train with RL. And so these are approximately the first half of the course. Um and then the second half of the course will be to do a project uh using these skills uh to you know do something kind of

[01:00:21.599] interesting or novel uh in whatever area you choose. And the project will be group based. So we're going to be uh asking you to form groups of two or three and uh and create a project. And the general schedule is uh we're going to talk about agent capabilities first.

[01:00:39.200] Um we're then going to jump into some specific domains like coding and guey agents. Um do uh training uh and uh including SFT and RL. Um we're going to be talking about uh frameworks and safety. And then uh we're going to be talking about interaction and then we have some project hours where everybody uh discusses their projects. And then uh on the end of the class we're going to

[01:01:05.520] try to get uh some domain experts from each of the various domains to give a guest lecture um which maybe combines a little bit of overview but also their research. Uh and so uh hopefully you'll be able to learn from uh some pretty exciting people. And I uh Daniel and I tried to brainstorm the best people in the uh in the world to talk about their

[01:01:25.280] things and I don't know if anybody said no. Um so I think everybody said yes. So uh we we got our first choice for every every topic. So I'm pretty excited about that. Um so uh before we begin uh we have some prerequisites and this is a heavy course in terms of implementation in machine learning. Uh we want uh we want everybody to be able to train an agent

[01:01:52.720] with RL by the end of it. And so our prerequisite is also um we require prior serious experience training a language model. Um the LTI courses on uh language models, language model systems, NLP would all qualify for this prerequisite. So if you took one of those, that's okay. Um some deep learning courses might qualify for it. Uh if you're not sure, um feel free to ask us. Um but we

[01:02:17.440] are going to require this and we're going to have everybody have to submit a form for it. So uh please uh please do do that. Um if there's like 30 people who want to know whether their course qualifies, please don't ask me that specific question after the class here because it'd be better to do it through email, but um uh other questions we'll be happy to answer after the class. Um

[01:02:39.599] we'll share a Google form on Patza and please submit the form so we can finalize enrollment. Um and uh yeah, I I already um uh I already covered it. If you haven't taken a course, if you've worked in industry and you've trained a model in industry, uh it should be a real one like at least 4 to 7B uh size, not uh not 100 million parameters. Um but we will also accept that.

[01:03:08.000] Um and so uh this is the grading policy. Um so assignments one to three will be 40% total uh completed individually. Um we're going to have lecture highlights and so uh basically the idea here is that we want people to uh come to the lecture and uh give a highlight about you know something you learned in the lecture.

[01:03:36.160] The idea around this is not to be, you know, not to make people do like undo work or something like this, but if you watch through the entire lecture, you hopefully you came up with something that's interesting. If you said if you could say nothing was interesting, I knew all of this already. I learned it here uh in this previous class that's already in the prerequisite list. That's

[01:03:58.720] also useful information for us. So share it with us. But hopefully we'll say at least one interesting thing in every lecture. So uh you can uh you can follow up with that. Um the research project uh is uh 50% of the total um and this will be in teams of two to three uh because it's uh half of the class assignments.

[01:04:18.240] Um the proposal is 5%, the check-in is 5%, presentation is 10% and final report is 30%. And if you've taken an LTI uh project based class before, grading will be similar to the LTI project based class uh requirements. Um if you have not then uh we'll we'll be sharing uh details about this.

[01:04:41.680] Um so here's the question uh you've all been asking for. This is an AI agent class. Um and we discussed this very um very thoroughly about what we wanted to do here. Um, I'd like to preface this by saying I use agents all the time for nearly everything I do. Um, but at the same time, it's kind of dangerous to use agents for everything because you lose

[01:05:09.599] like sight of uh of what you want to uh like of what you're learning. You miss some of the details and other things like this because the goal of this class is learning. Um but we also want everybody to be familiar with the standard practice. Um we uh we want you to keep this in mind and uh AI tools will be permitted um for basically everything in the course unless we say

[01:05:38.400] otherwise and we probably won't be saying otherwise very often. Um so uh lecture highlights must be written by you not generated by AI. Um and so these do not need to be long. Uh they can be short, they can be a few sentences, but please uh write them yourself. And uh you are responsible for every submitted claim, citation, result in line of code.

[01:06:02.079] And uh we will create quizzes uh for the assignments so that uh you will you may need to explain uh parts of your code. And uh how will we do this? Uh we also know how to use agents. So we will We we are considering having agents read uh read your code and come up with quiz questions tailored to your code. Um so uh we're we're serious about this. Uh

[01:06:31.359] and that means that the thousand lines of slop that your agent generated will be a bad idea for you to submit. Um so it's better to submit something concise that you really understand well uh than uh submitting you know more uh basically. Um, so yeah, uh, we're almost done. Uh, deadlines, uh, submissions in Slack. So, all the assignments, uh, include two

[01:06:54.160] 24-hour Slack days. Um, they cannot be transferred or shared. After the Slack days are used, the penalty is 5% of the assignment score per additional day or part day. So, what this means is the deadline is the deadline. And, uh, but we're being nice and if you miss the deadline, we'll give you some time to make up for it. uh if you miss the deadline by more than two days um then

[01:07:20.559] uh we're not going to take most excuses. If you you were in the hospital or something like that, we uh might ask you to get appropriate acknowledgement of that, but that would be an example uh reason why. Uh but other than that, please try to meet the deadline because we're not going to make many exceptions to this. Um cool, that's all. Uh we're at 441. Um so which means we have nine

[01:07:44.640] minutes for questions if people have questions. Um otherwise uh looking forward to having everybody in the class. Any Yes.

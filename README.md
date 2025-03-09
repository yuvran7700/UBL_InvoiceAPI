# 🕛 Git Setup & GitLab Crash Course <!-- omit in toc -->

- [1. Git Setup](#1-git-setup)
  - [1.1. Generating an SSH key and adding it to GitLab](#11-generating-an-ssh-key-and-adding-it-to-gitlab)
  - [1.2. Setting your Git Identity](#12-setting-your-git-identity)
- [2. Using Git and GitLab](#2-using-git-and-gitlab)
  - [2.1. Cloning](#21-cloning)
  - [2.2. Making a Commit](#22-making-a-commit)
  - [2.3. Working With Others](#23-working-with-others)
  - [2.4. Summary](#24-summary)
  - [2.5. Branching](#25-branching)
  - [2.6. Merging](#26-merging)
  - [2.7. Merge Conflicts](#27-merge-conflicts)
  - [2.8. Resolving a Merge Conflict](#28-resolving-a-merge-conflict)

# 1. Git Setup

> This will need to be done on any machine you want to git clone from.

You will need to have installed Git on your local machine if it doesn't already have it.

## 1.1. Generating an SSH key and adding it to GitLab

> You can skip this if you have already generated a key and added it to GitLab.

1. Run `ssh-keygen -t ed25519` in your terminal and hit enter until it stops prompting. Note the path where it is creating the key.
2. Navigate to the path where the key has been created. This will typically be in `~/.ssh`.
3. Print the public key to the terminal so it can be copied by running `cat ~/.ssh/id_ed25519.pub`

The key should look like the following:

```bash
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKkgchK4ok0W+GvU+q7jjnQ51dr2ztCowMxbwoFItT/h DESKTOP-ATFKE8N
```

> **NOTE: Do not share your private key with anyone**

4. Add the copied key to [https://nw-syd-gitlab.cseunsw.tech/-/profile/keys](https://nw-syd-gitlab.cseunsw.tech/-/profile/keys).

## 1.2. Setting your Git Identity

Whenever you make a commit, your current identity is associated with it.

To properly set up your identity so your commits are tagged with your name and email, run the following commands (replacing the place holders with your information)

```bash
git config --global user.name "Your Name"
git config --global user.email "yourName@student.unsw.edu.au"
```

# 2. Using Git and GitLab

> If you've taken COMP1531 recently and/or are relatively fluent in git, then feel free to move on and skip this.

## 2.1. Cloning

Cloning a _repository_ (a repository or repo is just a directory that is linked with git) copies to your computer all the files in the repo as well as a complete history of what changes, or _commits_, created those files. Cloning a repo is necessary before you can start making your own changes.

For each lab and assignment in this course, a repo will be created for you on _GitLab_. You will use it to store your work as you complete it. To clone this week's repo run:

```bash
git clone git@nw-syd-gitlab.cseunsw.tech:COMP2511/24T2/students/z5555555/lab01.git
```

## 2.2. Making a Commit

Now that you have cloned the repo, you are ready to work on the codebase locally.

A commit represents a set of changes to the files in a repository as well as a message describing those changes for human readers. A good use of git involves a lot of commits with detailed messages.

Before you can commit, you have to _stage_ your changes, effectively telling git what changes you actually want to commit and what changes you don't.

Making commits doesn't actually replicate your changes to the remote repository on GitLab. For that you need to _push_ your commits, uploading them to the remote server. When collaborating with others, it is important not only to commit frequently, but also to push often.

In general, the commands to commit and push are as follows:

```bash
git add [files_to_commit] # Stage
git commit -m"Detailed message describing the changes" # Commit
git push # Push
```

Follow these steps to see them in action:

1. Add a new file called `HelloWorld.java` in the repo directory
2. Add the following lines of code to the file using your favourite text editor and save.

```java
class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, Welcome to COMP2511!");
    }
}
```

3. Go back to your terminal and enter the following commands:

```bash
git add HelloWorld.java
git commit -m "Created first java program HelloWorld.java"
git push
```

4. **MAKE SURE YOU UNDERSTAND THE PURPOSE OF EACH OF THE 3 ABOVE COMMANDS!** If you are unsure about any of them, ask your tutor or lab assistant.
5. Go back to GitLab and confirm that your changes have been pushed to the server.

## 2.3. Working With Others

Usually when you are using git, it is in a team. That means that you will not be the only one who is making the changes. If someone else makes a change and pushes it to the server, your local repo will not have the most up-to-date version of the files. Luckily, git makes it easy to update our local copy with the `git pull` command.

This command checks the remote server that your local repo is linked to and makes sure that all of your files are up to date. This ensures that you don't accidentally do things like implement the same thing someone else has already done and also lets you use other people's work (e.g. new functions) when developing.

Pulling regularly is one of the **most important practices** in git!

Unfortunately, at the moment you are just working individually. But GitLab still gives us a nice way to practice a `git pull`.

## 2.4. Summary

1. View your repo on GitLab.
2. Click on the `HelloWorld.java` file
3. Click 'Edit' on the right-hand side.
4. Add a Java comment to the top of the file as shown below and click the 'Commit Changes' button at the bottom of the screen

```java
// A simple Java Program
```

5. This will have changed the `HelloWorld.java` file on the server but not on your local environment. To fetch these changes use the git pull command from your terminal
6. Confirm that your version of `HelloWorld.java` now has the changes you made on the web page

## 2.5. Branching

**Branches** are a vital part of git and are used so people can work on separate parts of the codebase and not interfere with one another or risk breaking a product that is visible to the client. Breaking something on one branch does not have an impact on any other.

Good use of git will involve separating parts of the project that can be worked on separately and having them in their own feature branch. These branches can then be merged when they are ready.

Useful commands for branches:

```bash
git checkout -b [new_branch_name] # Create a new branch and switch to it
git branch                        # List all current branches
git checkout [branch_name]        # Switch to an existing branch
```

Follow these instructions to create a branch:

1. Make your new branch with: `git checkout -b first_new_branch`
2. List your branches to see that you have indeed swapped (use the above commands)
3. Open the `HelloWorld.java` file and change the comment at the top of the file to Javadoc style comment as shown below:

```java
/**
* A simple java program that prints a hello world message to the console
*/
```

4. Try to push your changes to the server using the commands you learnt in the _Making a commit_ section
5. The above step should have given you the following error:

```
fatal: The current branch first_new_branch has no upstream branch.
```

This means that the branch you tried to make a change on doesn’t exist on the server yet which makes sense because we only created it on our local machine.

6. To fix this, we need to add a copy of our branch on the server and link them up so git knows that this new branch maps to a corresponding branch on the server

```bash
git push -u origin first_new_branch
```

**Note**: The final step only needs to be done for the first time you try to push using a new branch. After you have run this once, you should go back to simply using git push

## 2.6. Merging

Merging branches is used to combine the work done on two different branches and is where git's magic really comes in. Git will compare the changes done on both branches and decide (based on what changes were done to what sections of the file and when) what to keep. Merges are most often done when a feature branch is complete and ready to be integrated with the master branch.

Since we have finished all that we are going to do (and think there are no bugs) on our _first_new_branch_ we can merge it back into master.

**NOTE**: It is strongly recommended, both in this course and in general, to always ensure the code on the `master` branch compiles and is free of bugs. The latter is naturally harder to achieve than the former, but you should endeavour to keep master as _stable_ as possible.

Another recommendation is to merge master into your branch before merging your branch into master as this will ensure that any merge into master will go smoothly.

In general, merges are done by:

```bash
git merge [target] # Merge the target branch into current
```

**Note**: A successful merge automatically uses the commits from the source branch. This means that the commits have already been made, you just need to push these to the server (`git push`)

To merge your changes from above:

1. Switch back to the master branch using one of the commands from the above section
2. Merge in the changes you made in the other branch `git merge first_new_branch`
3. Push the successful merge to the server to update the master branch on the server

## 2.7. Merge Conflicts

Merge conflicts are the one necessary downside to git. Luckily, they can be avoided most of the time through good use of techniques like branches and regular commits, pushes and pulls. They happen when git cannot work out which particular change to a file you really want.

For this step we will engineer one so you can get a taste of what they are, how they occur and how to fix them. This will be the LAST time you will want one. The process may seem involved but it is quite common when multiple people are working at a time.

Follow these steps:

1. Change line 3 of `HelloWorld.java` to

```java
System.out.println("Hello, Welcome to Java!");
```

2. Add, commit and push your changes
3. Switch to your `first_new_branch`
4. Change line 3 of `HelloWorld.java`

```java
System.out.println("Hello, Welcome to merge conflicts!");
```

5. Add, commit and push your changes
6. Merge master into your current branch
7. This sequence of steps should make a merge conflict at the third line of `HelloWorld.java`

## 2.8. Resolving a Merge Conflict

Resolving a merge conflict is as simple as editing the file normally, choosing what you want to have in the places git wasn't sure.

A merge conflict is physically shown in the file in which it occurs. `<<<<<<<` marks the beginning of the conflicting changes made on the **current** (merged into) branch. `=======` marks the beginning of the conflicting changes made on the **target** (merged) branch. `>>>>>>>` marks the end of the conflict zone.

e.g.,

```
This line could be merged automatically.
There was no change here either
<<<<<<< current:sample.txt
Merges are too hard. This change was on the 'merged into' branch
=======
Merges are easy. This change was made on the 'merged' branch
>>>>>>> target:sample.txt
This is another line that could be merged automatically
```

This above example could be solved in many ways, one way would be to just use the changes made on the target branch and delete those made on the current branch. Once we have decided on this we just need to remove the syntax. The resolved file would be as follows

```
This line could be merged automatically.
There was no change here either
Merges are easy. This change was made on the 'merged' branch
This is another line that could be merged automatically
```

We would then just commit the resolved file and the merge conflict is finished!

To fix the conflict you created:

1. Open the `HelloWorld.java` file and decide which change you want to keep
2. Remove the merge conflict syntax
3. Add, commit and push the resolved merge conflict
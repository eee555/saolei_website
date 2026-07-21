# Contributing

This page is for students who are just starting to learn programming and may only have experience from school programming classes. You do not need to understand the whole website at first. If you can complete one small change and submit it to us, you are already contributing to open source.

## Where to Start

The best beginner contributions are usually small tasks, such as:

- Fixing typos in the documentation
- Adding a short explanation
- Improving Chinese or English text on a page
- Fixing a simple style problem
- Adding a screenshot
- Turning a problem you encountered into an Issue

At the beginning, we do not recommend changing complex features such as login, permissions, replay review, leaderboards, or tournament settlement.

## Software to Install

We recommend installing these tools:

| Software | Purpose |
| --- | --- |
| Git | Download code and save changes |
| VS Code | Edit code and documentation |
| Python | Run the backend |
| Node.js | Run the frontend and documentation |
| MySQL | Local database |
| Redis | Local cache |

If you only want to edit documentation, you usually only need:

- Git
- VS Code
- Node.js

## Downloading the Code

Open a terminal, choose a directory for the code, and run:

```bash
git clone https://github.com/eee555/saolei_website.git
cd saolei_website
```

If you plan to submit a Pull Request, we recommend clicking **Fork** on GitHub first, and then cloning your own repository.

## Editing Documentation Only

The documentation directory is:

```text
vitepress_doc
```

Enter the directory:

```bash
cd vitepress_doc
```

Install dependencies:

```bash
npm install
```

Start the documentation site:

```bash
npm run dev
```

Open this address in your browser:

```text
http://localhost:5173/docs/
```

After you edit Markdown files, the browser usually refreshes automatically.

Before submitting, we recommend running:

```bash
npm run build
```

If the build succeeds, the documentation probably has no obvious problems.

## Running the Frontend

If you want to change website pages, enter the frontend directory:

```bash
cd front_end
npm install
npm run dev
```

Open this address in your browser:

```text
http://localhost:8080
```

If you only change page styles or normal text, you can connect to the online server first:

```bash
npm run frontend
```

This lets you avoid configuring a local backend at the beginning.

## Running the Local Backend

If you want to change APIs, databases, login, replay upload, or similar features, you need to run the backend.

Enter the backend directory:

```bash
cd back_end/saolei
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.\.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

After preparing MySQL and Redis, run:

```bash
python manage.py makemigrations
python manage.py migrate userprofile
python manage.py migrate
python manage.py runserver --nostatic
```

The backend address is:

```text
http://127.0.0.1:8000
```

::: tip
Local backend setup is more likely to go wrong than documentation or frontend setup. If you only want to make your first contribution, starting with documentation or a small frontend change is easier.
:::

## Common Check Commands

Documentation:

```bash
cd vitepress_doc
npm run build
```

Frontend:

```bash
cd front_end
npm run lint
```

Backend:

```bash
cd back_end/saolei
python manage.py check
```

If you are not sure what to run, say so in the PR:

```text
I changed documentation and only ran npm run build.
```

## Submitting an Issue

Issues are used to report problems or suggest improvements.

A good Issue can include:

- The problem you encountered
- What you expected to happen
- What actually happened
- Steps to reproduce the problem
- Screenshots or error messages

Example:

```text
Title: The tournament page instructions are not clear enough

Problem:
When I first opened the tournament page, I did not know where to fill in the Arbiter identifier.

Expected:
I hope the documentation or page hint explains where to do it.

Screenshot:
...
```

## Submitting a Pull Request

Pull Request is usually shortened to PR. It is used to submit your changes to the project maintainers for review.

Basic process:

1. Fork the repository.
2. Clone your own repository.
3. Create a new branch.
4. Edit files.
5. Check locally.
6. Commit your changes.
7. Push to GitHub.
8. Create a PR on GitHub.

Common commands:

```bash
git checkout -b docs/fix-guide
git status
git add vitepress_doc/guide/some-file.md
git commit -m "docs: improve guide"
git push origin docs/fix-guide
```

You can write the PR description like this:

```text
## What changed
- Improved the explanation in the tournament documentation

## How to check
- npm run build
```

## If You Are Asked to Change Something

Maintainers may leave comments in the PR and ask you to change a few things. This is normal and does not mean you did a bad job.

You only need to:

1. Continue editing on the same branch.
2. Commit again.
3. Push again.

The original PR will update automatically.

## How to Ask Questions

When asking a question, try to include:

- What you are doing
- What command you ran
- The full error message
- Your system, such as Windows 11
- Where you think the problem might be

Instead of:

```text
It does not work. What should I do?
```

It is better to write:

```text
I failed to run npm install on Windows 11.
The directory is vitepress_doc.
The last few lines of the error are ...
I am not sure whether my Node.js version is too old.
```

This makes it much easier for others to help you.

## The Most Important Thing

Your first contribution does not need to be large. Fixing a typo, adding one sentence, or writing a clear Issue are all useful contributions.

Finish one small PR first, and you have already stepped into open source collaboration.

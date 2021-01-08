# Cultivating Whimsy: A Personal Blog

Over the years, I've started and abandoned many blogs and websites. I am not sure if the outcome will be different this time but it's 2021, the new year is just days old, and it was time to reclaim my identity and articulate my mission.


## Behind the Blog: Hugo

I've decided to build the blog using [Hugo](https://gohugo.io/). It's a static site generator that allows deployment of the built site to GitHub pages. 

Here are some of the reasons I picked it:

 * _Peer recommendations_: Many people I respect use Hugo and recommend it highly.
 * _Site Performance_: Hugo bills itself as the fastest framework for building websites. And this [Nov 2020 post](https://css-tricks.com/comparing-static-site-generator-build-times/) validated it with tests.
 * _Features & Flexibility_: I'll start with a basic/default setup but do want to leverage custom themes and extensions as I get familiar with this. Hugo's ecosystem is perfect here.
 * _Markdown FTW!_ I am a fan of Markdown and Hugo is too. Plus, with [shortcodes](https://gohugo.io/content-management/shortcodes/#readout), you get the power of custom templates alongside the simplicity of Markdown.

I'll write a post on my experience after a month or so. For now, here are the steps I've used to set this up:

 1. Followed the [quickstart](https://gohugo.io/getting-started/quick-start/) tutorial to setup the build system with default 'ananke' theme.
 2. Changed the default [build directory](https://gohugo.io/getting-started/quick-start/#step-7-build-static-pages) to `docs/` so it would build the site into that location within this repo. Now `hugo -D` in the root directory automatically builds the static site into `docs/`
 3. Updated Github [repo settings](https://github.com/nitya/nitya.github.io/settings) for `GitHub Pages` to use the '/docs' directory for building and deploying the static website.

TODO: 

Automate the build/deploy  workflow with [GitHub actions](https://github.com/features/actions) so the docs/ folder is updated automatically when new content or configuration changes occur.

Onwards!

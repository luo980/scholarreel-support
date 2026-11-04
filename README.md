# 研映 / ScholarReel Support

Public support and privacy pages for ScholarReel (研映), an iPhone and iPad research briefing app.

| Language | Support | Privacy |
| --- | --- | --- |
| 简体中文 | https://luo980.github.io/scholarreel-support/ | https://luo980.github.io/scholarreel-support/privacy/ |
| English | https://luo980.github.io/scholarreel-support/en/ | https://luo980.github.io/scholarreel-support/en/privacy/ |

Support: **luo980@gmail.com**. Developed and maintained by **luo980**.

## Build

```sh
python3 scripts/build.py
```

The build validates and copies the standalone HTML, CSS, and local assets from `site/` to `dist/`. Python 3 is the only build dependency. No application database, credentials, or iOS application source is included in this repository.

## Publish

GitHub Actions builds and deploys `main` to GitHub Pages. The repository's Pages source must be **GitHub Actions**. A workflow can also be started manually from Actions.

The site supports browsing with JavaScript disabled, includes no analytics scripts or forms, and uses local assets. GitHub Pages handles hosting and associated security access logs; see the published privacy policy for details.

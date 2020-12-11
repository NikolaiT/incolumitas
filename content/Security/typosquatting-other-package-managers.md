Title: What other package managers are vulnerable to typo squatting attacks?
Date: 2016-06-30 17:58
Modified: 2016-06-30 21:56
Author: Nikolai Tschacher
Category: Security
Tags: security, Typosquatting, nuget, cargo
Slug: what-other-package-managers-are-vulnerable-to-typosquatting
Status: published

In my last blog post about [typosquatting package managers]({filename}/Security/typosquatting-package-managers.md) I discussed my findings about attacking the programming language package managers from *rubygems.org, PyPi* and *npmjs.com*.

This blog contribution generated quite some interest and people subsequently asked themselves whether **other package managers
might also be vulnerable to this hybrid attack** (typosquatting involves a technical and psychological attack vector). During the time I wrote my thesis, I encountered some other package managers. A very good overview of some of the most recent package managers gives the [github showcase page](https://github.com/showcases/package-managers) about package managers which is summarized in the table below:

| Package Manager Name                                                          | # of Stars on Github |
|-------------------------------------------------------------------------------|----------------------|
| [bower/bower](https://github.com/bower/bower)                                 | 14257                |
| [VundleVim/Vundle.vim](https://github.com/VundleVim/Vundle.vim)               | 11969                |
| [npm/npm](https://github.com/npm/npm)                                         | 9664                 |
| [alcatraz/Alcatraz](https://github.com/alcatraz/Alcatraz)                     | 8936                 |
| [CocoaPods/CocoaPods](https://github.com/CocoaPods/CocoaPods)                 | 8115                 |
| [composer/composer](https://github.com/composer/composer)                     | 7909                 |
| [Carthage/Carthage](https://github.com/Carthage/Carthage)                     | 7160                 |
| [jordansissel/fpm](https://github.com/jordansissel/fpm)                       | 6722                 |
| [componentjs/component](https://github.com/componentjs/component)             | 4503                 |
| [apple/swift-package-manager](https://github.com/apple/swift-package-manager) | 4318                 |
| [wbond/package_control](https://github.com/wbond/package_control)             | 3018                 |
| [pypa/pip](https://github.com/pypa/pip)                                       | 2911                 |
| [chocolatey/chocolatey](https://github.com/chocolatey/chocolatey)             | 2741                 |
| [Masterminds/glide](https://github.com/Masterminds/glide)                     | 2163                 |
| [tmux-plugins/tpm](https://github.com/tmux-plugins/tpm)                       | 1961                 |
| [Homebrew/brew](https://github.com/Homebrew/brew)                             | 1757                 |
| [rust-lang/cargo](https://github.com/rust-lang/cargo)                         | 1705                 |
| [rubygems/rubygems](https://github.com/rubygems/rubygems)                     | 1547                 |
| [caolan/jam](https://github.com/caolan/jam)                                   | 1540                 |
| [volojs/volo](https://github.com/volojs/volo)                                 | 1326                 |
| [gpmgo/gopm](https://github.com/gpmgo/gopm)                                   | 1027                 |
| [spmjs/spm](https://github.com/spmjs/spm)                                     | 882                  |
| [atom/apm](https://github.com/atom/apm)                                       | 690                  |
| [freshshell/fresh](https://github.com/freshshell/fresh)                       | 674                  |
| [ruslo/hunter](https://github.com/ruslo/hunter)                               | 436                  |
| [ocaml/opam](https://github.com/ocaml/opam)                                   | 425                  |
| [NuGet/Home](https://github.com/NuGet/Home)                                   | 367                  |


The obvious question now is: How many of those package managers are vulnerable to typosquatting attacks. I stated three mandatory requirements that need to be fulfilled in order for those package repositories to be vulnerable for typosquatting attacks. Those were:

1. The possibility of registering **any package name and uploading code without any hard costs** such as providing a real identity or registering a domain name.
2. The feasibility to **achieve code execution upon package installation** on the host system. This requirement is not absolutely needed since code may also be executed when the typo package is finally imported.
3. Accessibility and presence of **good documentation** for uploading and distributing packages
on the package repository. Plus: Flat learning curve to quickly develop a demo program in the target programming language.


## Package managers that are not vulnerable
A good approach seems to be studying package managers that were found to be not vulnerable to typosquatting attacks and identify
the critical differences that makes one package manager attackable and the other not. In my thesis, I initially wanted to also attack the repositories

- [Bower](https://bower.io/)
- [Packagist](https://packagist.org/)
- [CPAN](http://www.cpan.org/)

and found good reasons and obstacles to not include them in my attack.

#### Bower

There is a [long discussion on github](https://github.com/bower/bower/issues/249) whether to allow pre- and post-install hooks similiar to the ones used in *npm*. **Sheerun** commented on *Apr 16, 2014* in a github issues discussion:

> This is utterly wrong idea... Allowing postinstall raises serious security issues. With them anyone is able to run arbitrary code on your computer and on your production machines... That's why it's impossible in tools like git to commit any hooks to repository. Bower is git of web.

> This is especially dangerous in case of bower as it doesn't use any checksums, or packaging. A lot of people are depending on branches which can change in any moment (as well as tags btw.).

> As @necolas pointed out postinstall is also useless to post-process files as user environment is unknown and unpredictable. Bower is going to have publish command so pre-publish hook will be ok.

> If hooks are implemented, they should be immediately reverted and deprecated.

**Sheerun** also mentioned:

> If anyone want to compare with npm:

> With npm post-install is more acceptable (still bad idea) because you can't avoid executing javascript files on server. Bower is different story as packages are executed only in web browser. Also npm has checksums, packaged packages, projects like https://nodesecurity.io/.

> Moreover bower is used not only by node projects. This "feature" makes any project using bower directly vulnerable (like https://github.com/42dev/bower-rails or https://github.com/d-i/half-pipe or bower CDNs).

This comment explains the exact reasons why a package manager shouldn't have pre/post install functionality. Additionally, there are a few points that make *Bower* very attractive to an attack:

- The Bower registry does not have authentication or user management at this point in time. It’s on a first come, first served basis.

- Bower doesn’t support GitHub-style namespacing (org/repo)

While I didn't find a way to achieve code execution on installation time in *Bower*, it is perfectly possible to spread typo squatted packages with other files than the intended front end files (like *.css, .js or .html* files). Just imagine to bypass security by typosquatting the popular *jQuery* library and adding some PHP files with exploit code that is triggered as soon as the manipulated *jQuery* library is loaded in a browser. This exploits the fact that libraries installed over *Bower* often find their way to servers and can thus be interpreted as a server side scripting language if the webserver is configured accordingly.


#### CPAN
The *CPAN* ecosystem was simply too complex and cumbersome to try to attack. The declining popularity of *CPAN* and Perl in the past years was another reason to exclude it from research. It might be the case that *CPAN* is vulnerable to typosquatting attacks. Can anyone familiar with the Perl ecosystem confirm this?

#### Packagist (PHP)
*Packagist (PHP)* is not vulnerable to direct code execution upon package installation, because all installed packages are stored as dependency in sub folders, which are never directly touched. I tried to attack *Packagist* but couldn't find any way to achieve code execution on installation time. Maybe anyone familiar with the PHP ecosystem can double check this?

## Discussions about potentially vulnearble package managers

After I published my last blog post, several discussions emerged in package management communities about the security of their repositories in regard to the typosquatting attack.

#### Rust(Cargo)

The relatively new programming language *Rust* has also a third party library repository which is named *Cargo*. The publication of my blog post provoked a discussion in a the [rust subreddit](https://www.reddit.com/r/rust/comments/4n5zrj/typosquatting_programming_language_package/).
[A user](https://www.reddit.com/r/rust/comments/4n5zrj/typosquatting_programming_language_package/d416n75) mentions that Cargo lets you run arbitrary code on startup:

> **Cargo lets packages run arbitrary code on startup.** This is pretty useful and important.
> I wonder if we can use a sandbox model for this - don't let cargo scripts touch anything outside of the code directory.
> Still dangerous but at least you don't have arbitrary read/write access.
> I would imagine it is not idiomatic to install dependency packages for cargo scripts.

[Another user](https://www.reddit.com/r/rust/comments/4n5zrj/typosquatting_programming_language_package/d416ic8) also confirms that *Cargo* might be affected by this vulnerability:

> This could affect crates.io (yay buildscripts!) AFAICT. However there are some important caveats with cargo.
> For one thing, dependencies are added by editing a file, and CLI tools for including deps are third-party.
> IME, I and others are more careful with typos in an editor than on the command line.
> Further, my usual practice is to copy/paste the toml line from the crates.io page, and then remove the patch version.
> But maybe that's not typical? Regardless, there's no tool for system-wide installation like pip or npm has, so it seems to me like there's
> likely to be more intention behind adding a crate dependency.
> Also, crates don't execute buildscripts when you add them to your Cargo.toml
> (whether or not you use a tool like cargo edit), buildscripts run when you actually build your project,
> so there's more chance you'll find the typo in between typing it and when malicious code could run.

The same user also states that it doesn't seem feasible to remove the code execution on installation:

> The first doesn't seem practical because a) **cargo supports arbitrary code execution in tests/benches anyways** (duh) b) it'd be crappy to deprecate and c) it's really important for FFI crates and stable alternatives to compiler plugins.

Another posted suggestion was to add an option to the package manager to allow running build scripts:

> I don't like auto-exec'ing buildscripts. But buildscripts are incredibly useful.
> For cargo, we could simply stop automatically executing the buildscripts. At the same time, provide a switch called --dangerously-exec-buildscript or something else equally instructive.
> Then, if I'm sure I know what I'm doing, I can do cargo install foo --dangerously-exec-buildscript

I will examine *Cargo* in a next blog post closer and see whether it is vulnerable to typo squatting attacks by myself.

#### Archlinux

Archlinux is actually a Linux distribution, not a programming language. There was also a [discussion](https://www.reddit.com/r/archlinux/comments/4n5e6a/typosquatting_programming_language_package/) in the archlinux subreddit about the security implications for letting users submit 
own packages. A user essentially confirms that Archlinux and its PKGBUILD's are affected by typosquatting package managers by saying:

> Though package managers encourage you to read the pkgbuild and install. So if someone does read it, you can't just hide malicious install commands, you have to actually make your own github repo or something, and push malicious builds to there.

## Package managers that will be examined closer in upcoming blog posts

I will definitely examine the following package managers closer in the future. For *Nuget* I will need to install a Windows operating system and Visual Studio in order to test the upload
process manually. I hope that I don't need a Apple Operating system when trying to attack the swift language. Rust should work fine on Linux systems.

- [Nuget C# .NET ](https://www.nuget.org/)
- [Cargo Rust](https://github.com/rust-lang/cargo)
- [apple/swift-package-manager](https://github.com/apple/swift-package-manager)

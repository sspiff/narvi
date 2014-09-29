narvi
=====

_DRAFT: Not all of this is implemented_

narvi is a deterministic password generator, similar in concept to [PwdHash](http://crypto.stanford.edu/PwdHash/).  The goal is to help you reduce the number of passwords that you have to remember while still providing a different password for every account.

To use it, you provide narvi with an account identifier, such as `you@mail.com`, and your "master" password.  narvi will produce an account-specific password based on a hash of the combination of the account identifier and your master password.  Changing the account identifier, or _salt_, while keeping the master password the same will yield a different account password.  narvi does not store the passwords; it generates them each time you need them.

## Features

* Uses scrypt as its hashing function, with configurable hashing parameters.
* Arbitrary, user-defined account identification (salt).
* Supports multiple word schemes to support various password policies.
* Portable command line utility written in Python that runs on any system with Python (>= 2.6 and < 3).
* Distributed as a single, OS-agnostic file (zipped Python).
* Includes fast, native scrypt libraries for Windows, Mac, and Linux, with a pure Python implementation for other systems.

## Basic Usage

When run with no parameters, narvi will prompt you for a salt, for which you can use any value, but which should typically be some account identifier, such as `you@yourbank.com`.  If it is a salt that narvi recognizes, it will prompt you for the master password, generate the hash, and "output" the account-specific password.  On Windows and Mac, narvi will make the password available in the clipboard for eight seconds.  On Linux, narvi will output the password to stdout.

If the salt is not one that narvi recognizes, it will prompt you for the configuration for that salt:
* The hash scheme (defaults to scrypt with N=2^18, r=8, p=1)
* The word scheme (defaults to a 16-character base64-encoded password using ! and @ as the extra characters, with at least one lower case, one upper case, and one digit)
* A description (default is none)

## Thoughts on Master Passwords

Consider using a six-word (at least) [Diceware](http://world.std.com/~reinhold/diceware.html) passphrase.

## Thoughts on Salt Construction

Start with `USERNAME @ WEBSITE`, such as `you@yourbank.com`.  This will make it easier to remember the salt if you switch to a new computer or otherwise lose your remembered salts.

If a service requires that you regularly change your password, append a date:
```
USERNAME @ WEBSITE # DATE
you@yourbank.com#2014
you@yourbank.com#3Q14
```

If a service requires security questions, consider using a narvi-generated password for these as well.  In this way, you will not be providing the same answers to multiple services.
```
USERNAME @ WEBSITE , QUESTION
you@yourbank.com,mothersmaiden
```

## Regarding Security

_The author is not a subject matter expert in cryptography.  Read the paper, convince yourself (or not)._

scrypt is designed such that even if an attacker knows: your salt, the scrypt hash function parameters, and the hash output, then discovering your master password is still "hard".  The security lies in the scrypt key derivation algorithm and the entropy in your master password, not in the secrecy of your salts.

Scrypt is described in detail in [Stronger Key Derivation via Sequential Memory-Hard Functions](http://www.tarsnap.com/scrypt/scrypt.pdf).

Using one-way hashes as service-specific passwords is not new.  See, for example, [A Convenient Method for Securely Managing Passwords](https://jhalderm.com/pub/papers/password-www05.pdf) and [Stronger Password Authentication Using Browser Extensions](http://crypto.stanford.edu/PwdHash/pwdhash.pdf).

## Other narvi Commands

* To generate the password for a salt given on the command line: `narvi hash SALT`
* To list the remembered salts: `narvi list`
* To forget a remembered salt: `narvi forget SALT`
* To list available hash schemes: `narvi lshashschemes`
* To list available word schemes: `narvi lswordschemes`
* To view the license: `narvi license`

## Misc Details

narvi stores some stuff in `~/.narvi/`.  In particular, its saved configuration is in `~/.narvi/config` as JSON.


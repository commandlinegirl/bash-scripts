### Useful one-liners in bash (examples)

Move a long list of files to a target dir (solution to "/bin/mv: Argument list too long")

```
find $(pwd) -maxdepth 1 -name "*.png" | xargs -I {} mv {} /path/to/target
```

Get the number of lines of code in a git repo
```
git ls-files jupyterlab | xargs wc -l
```

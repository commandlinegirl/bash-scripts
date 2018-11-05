### Useful one-liners in bash (examples)

Move a long list of files to a target dir (solution to "/bin/mv: Argument list too long")

```
find $(pwd) -name "*.png" | xargs -I {} mv {} /path/to/target
```

# SemiTO-V Micropython Compatibility Layer
## How to build
```shell
git clone <nome-repository>
```
## How to use
``` python
from <nome-modulo> import MiddleLayer
```
### Add a module in Micropython
``` python
ml = MiddleLayer()
ml.add("<ModuleName>")
ml.add_from("<ModuleObject>","<ModuleName>")
```
### Add a variable in Micropython
``` python
ml.set_value("<variableName>","<rValue>") #Create it
<variableName>.<methodName> #Use it
```
After creating (or setting) a variable you will be able to use it as a normal one.
**Note**: It will be added to the _global_ scope.
## How to contribute
In order to contribute, **first check the opened issues** and choose one. 
All the new code that fixes something or implements a new feature must be pushed on a **new branch** with the **name of the issue that is fixing**. 
Only after it will be merged into the **develop branch**.
**DO NOT PUSH ON THE MASTER BRANCH**.
If you want to push new code and no issue match with it, **create a new one first**.
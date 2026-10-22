"""Verify the post-review motion change affects only its module documentation."""
import ast,hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4];name='runtime/original_match/port/motion.py';oldhead='3ef56c53048b194cad0b370bccff880bb6e1e73f'
old=subprocess.check_output(['git','show',oldhead+':'+name],cwd=root);new=(root/name).read_bytes()
a,b=ast.parse(old),ast.parse(new)
for tree in (a,b):
 assert isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) and isinstance(tree.body[0].value.value,str)
 tree.body=tree.body[1:]
assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
changed=subprocess.check_output(['git','diff','--name-only',oldhead,'--','runtime','tests','tools'],cwd=root,text=True).splitlines()
assert changed==[name],changed
print(json.dumps({'oldhead':oldhead,'motion_before_sha256':hashlib.sha256(old).hexdigest(),'motion_after_sha256':hashlib.sha256(new).hexdigest(),'only_runtime_diff':name,'executable_AST_identical_excluding_module_docstring':True},indent=2))

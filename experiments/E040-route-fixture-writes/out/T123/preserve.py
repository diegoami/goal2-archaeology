"""Static before-source preservation, including expanded normal Match constructor."""
import ast,hashlib,json,subprocess,sys,types
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT/'runtime'))
BASE='62289f17e3386560537cb32804799765a437cb59'
paths=['runtime/original_match/route.py','runtime/original_match/match.py']+[f'runtime/original_match/port/{name}.py' for name in ('route','silent','display','entrypoints')]
def functions(tree,prefix=''):
    out={}
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):out[prefix+node.name]=node
        elif isinstance(node,ast.ClassDef):out.update(functions(node,prefix+node.name+'.'))
    return out
rows=[];registries={}
from original_match import port
for path in paths:
    old_source=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT,text=True)
    new_source=(ROOT/path).read_text();old=functions(ast.parse(old_source));current=functions(ast.parse(new_source))
    for name,node in old.items():
        actual=current[name]
        if name=='Match.__init__':
            helper=current['Match._initialize_session'];replacement=helper.body[1:]
            expanded=[]
            for statement in actual.body:
                if isinstance(statement,ast.Expr) and isinstance(statement.value,ast.Call) and isinstance(statement.value.func,ast.Attribute) and statement.value.func.attr=='_initialize_session':expanded.extend(replacement)
                else:expanded.append(statement)
            actual.body=expanded
        assert ast.dump(node,include_attributes=False)==ast.dump(actual,include_attributes=False),(path,name)
    rows.append({'path':path,'old_function_count':len(old),'unchanged_ast_including_expanded_normal_constructor':True,
                 'before_sha256':hashlib.sha256(old_source.encode()).hexdigest(),'current_sha256':hashlib.sha256(new_source.encode()).hexdigest()})
    if '/port/' in path:
        name=Path(path).stem;module=types.ModuleType('_t123_old_'+name);module.__package__='original_match.port';module.__file__=str(ROOT/path)
        exec(compile(old_source,module.__file__,'exec'),module.__dict__)
        reg=port._module_registry(name);old_reg=module.PORTS
        for address,entry in old_reg.entries.items():
            actual=reg.entries[address]
            assert (entry.ret,entry.far,entry.pop,entry.long,entry.return_stack_delta)==(actual.ret,actual.far,actual.pop,actual.long,actual.return_stack_delta),(name,address)
        registries[name]={'preserved_old_entries':len(old_reg.entries),'added_entries':sorted(set(reg.entries)-set(old_reg.entries)),'preserved_old_variants':sorted(old_reg.variants)}
print(json.dumps({'status':'passed','before_commit':BASE,'source_audits':rows,'registries':registries},sort_keys=True,indent=2))

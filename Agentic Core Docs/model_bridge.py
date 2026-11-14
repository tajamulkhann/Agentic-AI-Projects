"""Optional hosted LLM planner. Model output is *advisory*, never executable code.

This is deliberately excluded from offline benchmark results. Requires explicit
--model-plan or the Streamlit option, plus OPENAI_API_KEY in the environment.
"""
import json
import os
import urllib.error
import urllib.request


def validate_plan(plan, tool_names):
    """Reject tools absent from the explicit allowlist and malformed model output."""
    allowed=set(tool_names)
    if not isinstance(plan,dict) or not isinstance(plan.get('steps'),list):
        raise ValueError('Expected a JSON object containing a steps array')
    names=[]
    for step in plan['steps']:
        if not isinstance(step,str) or step not in allowed:
            raise ValueError(f'LLM proposed an unavailable tool: {step!r}')
        if step not in names:names.append(step)
    if len(names)>len(allowed):raise ValueError('LLM plan too long')
    return names


def suggest_plan(request:dict, tool_names:list[str], *, opener=None):
    """Ask a hosted LLM to suggest an allowed tool order, without executing tools.

    Only the supplied request object and allowed tool names are sent externally.
    No output, local files, credentials or synthetic evidence corpus is transmitted.
    Returns token usage from the API if provided; dollar cost is not estimated.
    """
    api_key=os.environ.get('OPENAI_API_KEY','').strip()
    if not api_key:raise RuntimeError('Set OPENAI_API_KEY before requesting hosted model planning')
    if not tool_names:raise ValueError('No tools in allowlist')
    model=os.environ.get('OPENAI_MODEL','gpt-4.1-mini')
    instructions=(
        'You are an engineering planner. Output one JSON object with a steps array of tool names. '
        'Each step must be EXACTLY one of the provided allowed tools. Never add new tools, '
        'credentials, shell commands or steps that change records. Keep the plan concise. '
        'This is advisory only: the real agent follows its own trusted tool policy.'
    )
    body={'model':model,'temperature':0,'response_format':{'type':'json_object'},
          'messages':[{'role':'system','content':instructions},
                      {'role':'user','content':json.dumps({'request':request,'allowed_tools':tool_names})}]}
    req=urllib.request.Request('https://api.openai.com/v1/chat/completions',
        data=json.dumps(body).encode('utf-8'),
        headers={'Authorization':'Bearer '+api_key,'Content-Type':'application/json'},
        method='POST')
    transport=opener or urllib.request.urlopen
    with transport(req,timeout=35) as response:
        result=json.loads(response.read().decode('utf-8'))
    content=result['choices'][0]['message']['content']
    proposed=json.loads(content)
    steps=validate_plan(proposed,tool_names)
    return {'advisory_steps':steps,'model':result.get('model',model),
            'api_usage':result.get('usage',{}),
            'model_api_cost_usd':None,
            'warning':'Hosted model advice only. Dollar charge not calculated. Execution remains policy controlled.'}

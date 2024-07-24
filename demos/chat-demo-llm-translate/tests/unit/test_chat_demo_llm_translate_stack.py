import aws_cdk as core
import aws_cdk.assertions as assertions

from chat_demo_llm_translate.chat_demo_llm_translate_stack import ChatDemoLlmTranslateStack

# example tests. To run these tests, uncomment this file along with the example
# resource in chat_demo_llm_translate/chat_demo_llm_translate_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ChatDemoLlmTranslateStack(app, "chat-demo-llm-translate")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

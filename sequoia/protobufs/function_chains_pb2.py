# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: function_chains.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='function_chains.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x15\x66unction_chains.proto\")\n\x0eLambdaFunction\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\x05\"\xdc\x01\n\tChainNode\x12!\n\x08\x66unction\x18\x01 \x01(\x0b\x32\x0f.LambdaFunction\x12\x0e\n\x06nodeID\x18\x02 \x01(\x05\x12\x1c\n\x08\x63hildren\x18\x03 \x03(\x0b\x32\n.ChainNode\x12\x13\n\x0blastNodeIDs\x18\x04 \x03(\x05\x12\x18\n\x10\x63hainFunctionIDs\x18\x05 \x03(\x05\x12\"\n\x04\x61rgs\x18\x06 \x03(\x0b\x32\x14.ChainNode.ArgsEntry\x1a+\n\tArgsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\xbb\x01\n\nChainState\x12\x1f\n\x0b\x63urrentNode\x18\x01 \x01(\x0b\x32\n.ChainNode\x12\x12\n\ninstanceID\x18\x02 \x01(\x05\x12\x0f\n\x07\x63hainID\x18\x03 \x01(\x05\x12%\n\x05\x66lags\x18\x04 \x03(\x0b\x32\x16.ChainState.FlagsEntry\x12\x12\n\ninvokeTime\x18\x05 \x01(\t\x1a,\n\nFlagsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x62\x06proto3')
)




_LAMBDAFUNCTION = _descriptor.Descriptor(
  name='LambdaFunction',
  full_name='LambdaFunction',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='url', full_name='LambdaFunction.url', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='id', full_name='LambdaFunction.id', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=25,
  serialized_end=66,
)


_CHAINNODE_ARGSENTRY = _descriptor.Descriptor(
  name='ArgsEntry',
  full_name='ChainNode.ArgsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='ChainNode.ArgsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='ChainNode.ArgsEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=246,
  serialized_end=289,
)

_CHAINNODE = _descriptor.Descriptor(
  name='ChainNode',
  full_name='ChainNode',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='function', full_name='ChainNode.function', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='nodeID', full_name='ChainNode.nodeID', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='children', full_name='ChainNode.children', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='lastNodeIDs', full_name='ChainNode.lastNodeIDs', index=3,
      number=4, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='chainFunctionIDs', full_name='ChainNode.chainFunctionIDs', index=4,
      number=5, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='args', full_name='ChainNode.args', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_CHAINNODE_ARGSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=69,
  serialized_end=289,
)


_CHAINSTATE_FLAGSENTRY = _descriptor.Descriptor(
  name='FlagsEntry',
  full_name='ChainState.FlagsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='ChainState.FlagsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='ChainState.FlagsEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=435,
  serialized_end=479,
)

_CHAINSTATE = _descriptor.Descriptor(
  name='ChainState',
  full_name='ChainState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='currentNode', full_name='ChainState.currentNode', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='instanceID', full_name='ChainState.instanceID', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='chainID', full_name='ChainState.chainID', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='flags', full_name='ChainState.flags', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='invokeTime', full_name='ChainState.invokeTime', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_CHAINSTATE_FLAGSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=292,
  serialized_end=479,
)

_CHAINNODE_ARGSENTRY.containing_type = _CHAINNODE
_CHAINNODE.fields_by_name['function'].message_type = _LAMBDAFUNCTION
_CHAINNODE.fields_by_name['children'].message_type = _CHAINNODE
_CHAINNODE.fields_by_name['args'].message_type = _CHAINNODE_ARGSENTRY
_CHAINSTATE_FLAGSENTRY.containing_type = _CHAINSTATE
_CHAINSTATE.fields_by_name['currentNode'].message_type = _CHAINNODE
_CHAINSTATE.fields_by_name['flags'].message_type = _CHAINSTATE_FLAGSENTRY
DESCRIPTOR.message_types_by_name['LambdaFunction'] = _LAMBDAFUNCTION
DESCRIPTOR.message_types_by_name['ChainNode'] = _CHAINNODE
DESCRIPTOR.message_types_by_name['ChainState'] = _CHAINSTATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LambdaFunction = _reflection.GeneratedProtocolMessageType('LambdaFunction', (_message.Message,), dict(
  DESCRIPTOR = _LAMBDAFUNCTION,
  __module__ = 'function_chains_pb2'
  # @@protoc_insertion_point(class_scope:LambdaFunction)
  ))
_sym_db.RegisterMessage(LambdaFunction)

ChainNode = _reflection.GeneratedProtocolMessageType('ChainNode', (_message.Message,), dict(

  ArgsEntry = _reflection.GeneratedProtocolMessageType('ArgsEntry', (_message.Message,), dict(
    DESCRIPTOR = _CHAINNODE_ARGSENTRY,
    __module__ = 'function_chains_pb2'
    # @@protoc_insertion_point(class_scope:ChainNode.ArgsEntry)
    ))
  ,
  DESCRIPTOR = _CHAINNODE,
  __module__ = 'function_chains_pb2'
  # @@protoc_insertion_point(class_scope:ChainNode)
  ))
_sym_db.RegisterMessage(ChainNode)
_sym_db.RegisterMessage(ChainNode.ArgsEntry)

ChainState = _reflection.GeneratedProtocolMessageType('ChainState', (_message.Message,), dict(

  FlagsEntry = _reflection.GeneratedProtocolMessageType('FlagsEntry', (_message.Message,), dict(
    DESCRIPTOR = _CHAINSTATE_FLAGSENTRY,
    __module__ = 'function_chains_pb2'
    # @@protoc_insertion_point(class_scope:ChainState.FlagsEntry)
    ))
  ,
  DESCRIPTOR = _CHAINSTATE,
  __module__ = 'function_chains_pb2'
  # @@protoc_insertion_point(class_scope:ChainState)
  ))
_sym_db.RegisterMessage(ChainState)
_sym_db.RegisterMessage(ChainState.FlagsEntry)


_CHAINNODE_ARGSENTRY._options = None
_CHAINSTATE_FLAGSENTRY._options = None
# @@protoc_insertion_point(module_scope)

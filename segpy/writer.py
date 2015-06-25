from segpy.encoding import ASCII, is_supported_encoding, UnsupportedEncodingError
from segpy.toolkit import (write_textual_reel_header, write_binary_reel_header, compile_trace_header_format,
                           write_trace_header, write_trace_samples, format_extended_textual_header,
                           write_extended_textual_headers)


def write_segy_based_on(fh, segy_object, data_block, encoding=None, endian='>', progress=None):
    write_structure(fh, segy_object, encoding, endian, progress)
    write_traces_from_data_block(fh, segy_object, data_block, endian, progress)
    
def write_structure(fh,
               segy_object,
               encoding=None,
               endian='>',
               progress=None):
    encoding = encoding or (hasattr(segy_object, 'encoding') and segy_object.encoding) or ASCII
    if not is_supported_encoding(encoding):
        raise UnsupportedEncodingError("Writing SEG Y", encoding)
    write_textual_reel_header(fh, segy_object.textual_reel_header, encoding)
    write_binary_reel_header(fh, segy_object.binary_reel_header, endian)
    write_extended_textual_headers(fh, segy_object.extended_textual_header, encoding)

def write_traces_from_data_block(fh,
                                 segy_object,
                                 data_block,
                                 endian='>',
                                 progress=None):
    trace_header_format = compile_trace_header_format(endian)
    
    trace_length = data_block.shape[0]
    if segy_object.max_num_trace_samples() != trace_length:
        raise ValueError("trace length of data block does not match the segy_object's", segy_object.max_num_trace_samples(), trace_length)
    
    num_traces = data_block.shape[1]        
    if data_block.ndim == 3:
        num_traces *= data_block.shape[2]
    if segy_object.num_traces() != num_traces:
        raise ValueError("number of traces in data block does not match the segy_object's")
        
    trace_data = data_block.reshape((trace_length, num_traces))
    trace_header_format = compile_trace_header_format(endian)
    for trace_index in segy_object.trace_indexes():
        write_trace_header(fh, segy_object.trace_header(trace_index), trace_header_format)
        write_trace_samples(fh, trace_data[:,trace_index], segy_object.data_sample_format, endian=endian)

def write_traces(fh,
           segy_object,
           encoding=None,
           endian='>',
           progress=None):
    trace_header_format = compile_trace_header_format(endian) 
    for trace_index in segy_object.trace_indexes():
        write_trace_header(fh, segy_object.trace_header(trace_index), trace_header_format)
        write_trace_samples(fh, segy_object.trace_samples(trace_index), segy_object.data_sample_format, endian=endian)
    
        
def write_segy(fh,
               seg_y_data,
               encoding=None,
               endian='>',
               progress=None):
    """
    Args:
        fh: A file-like object open for binary write.

        seg_y_data:  An object from which the headers and trace_samples data can be retrieved. Requires the following
            properties and methods:
              seg_y_data.textual_reel_header
              seg_y_data.binary_reel_header
              seg_y_data.extended_textual_header
              seg_y_data.trace_indexes
              seg_y_data.trace_header(trace_index)
              seg_y_data.trace_samples(trace_index)

              seg_y_data.encoding
              seg_y_data.endian

              One such legitimate object would be a SegYReader instance.

        encoding: Optional encoding for text data. Typically 'cp037' for EBCDIC or 'ascii' for ASCII. If omitted, the
            seg_y_data object will be queries for an encoding property.

        endian: Big endian by default. If omitted, the seg_y_data object will be queried for an encoding property.

        progress: An optional progress bar object.

    Raises:
        UnsupportedEncodingError: If the specified encoding is neither ASCII nor EBCDIC
        UnicodeError: If textual data provided cannot be encoded into the required encoding.
    """

    write_structure(fh, seg_y_data, encoding, endian, progress)
    write_traces(fh, seg_y_data, encoding, endian, progress)
    
#     encoding = encoding or (hasattr(seg_y_data, 'encoding') and seg_y_data.encoding) or ASCII
#     if not is_supported_encoding(encoding):
#         raise UnsupportedEncodingError("Writing SEG Y", encoding)
#     write_textual_reel_header(fh, seg_y_data.textual_reel_header, encoding)
#     write_binary_reel_header(fh, seg_y_data.binary_reel_header, endian)
#     write_extended_textual_headers(fh, seg_y_data.extended_textual_header, encoding)
#     trace_header_format = compile_trace_header_format(endian)
#     for trace_index in seg_y_data.trace_indexes():
#         write_trace_header(fh, seg_y_data.trace_header(trace_index), trace_header_format)
#         write_trace_samples(fh, seg_y_data.trace_samples(trace_index), seg_y_data.data_sample_format, endian=endian)

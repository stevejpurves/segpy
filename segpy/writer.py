from segpy.encoding import ASCII, is_supported_encoding, UnsupportedEncodingError
from segpy.packer import HeaderPacker
from segpy.trace_header import TraceHeaderRev1
from segpy.toolkit import (write_textual_reel_header, write_binary_reel_header,
                           write_trace_header, write_trace_samples,
                           write_extended_textual_headers)


def write_segy_based_on(hf, segy_y_reader, data, endian='>'):
  """
  Purpose:
    make it easy to write new (processed) data back to a new segy file based on the original
    segy file

  Args:
    fh: A file-like object open for binary write.

    segy_y_reader: a SegYReader instance from which the segy headers and other parameters can be retreived

    data: a numpy array containing trace samples organised in (trace, inline, crossline order)

  """

  encoding = segy_y_reader.encoding

  if not is_supported_encoding(encoding):
      raise UnsupportedEncodingError("Writing SEG Y", encoding)

  write_textual_reel_header(fh, segy_y_reader.textual_reel_header, encoding)
  write_binary_reel_header(fh, segy_y_reader.binary_reel_header, endian)
  write_extended_textual_headers(fh, segy_y_reader.extended_textual_header, encoding)

  trace_header_packer = HeaderPacker(trace_header_format, endian)

  il_xl = list(itertools.product(segy_y_reader.inline_range(), segy_y_reader.xline_range()))
  x_y = list(itertools.product(range(0,segy_y_reader.num_inlines()), range(0,segy_y_reader.num_xlines())))
  for ix,ij in zip(il_xl, x_y):
      idx = reader.trace_index((ix[0],ix[1]))
      write_trace_header(fh, segy_y_reader.trace_header(idx), trace_header_packer)
      write_trace_samples(fh, data[:,ij[0],ij[1]], segy_y_reader.data_sample_format, endian=endian)



def write_segy(fh,
               seg_y_data,
               encoding=None,
               trace_header_format=TraceHeaderRev1,
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

        trace_header_format: The class which defines the layout of the trace header. Defaults to TraceHeaderRev1.

        encoding: Optional encoding for text data. Typically 'cp037' for EBCDIC or 'ascii' for ASCII. If omitted, the
            seg_y_data object will be queries for an encoding property.

        endian: Big endian by default. If omitted, the seg_y_data object will be queried for an encoding property.

        progress: An optional progress bar object.

    Raises:
        UnsupportedEncodingError: If the specified encoding is neither ASCII nor EBCDIC
        UnicodeError: If textual data provided cannot be encoded into the required encoding.
    """

    encoding = encoding or (hasattr(seg_y_data, 'encoding') and seg_y_data.encoding) or ASCII

    if not is_supported_encoding(encoding):
        raise UnsupportedEncodingError("Writing SEG Y", encoding)

    write_textual_reel_header(fh, seg_y_data.textual_reel_header, encoding)
    write_binary_reel_header(fh, seg_y_data.binary_reel_header, endian)
    write_extended_textual_headers(fh, seg_y_data.extended_textual_header, encoding)

    trace_header_packer = HeaderPacker(trace_header_format, endian)

    for trace_index in seg_y_data.trace_indexes():
        write_trace_header(fh, seg_y_data.trace_header(trace_index), trace_header_packer)
        write_trace_samples(fh, seg_y_data.trace_samples(trace_index), seg_y_data.data_sample_format, endian=endian)

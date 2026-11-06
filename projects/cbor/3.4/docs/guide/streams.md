---
description: Where a decoder reads its bytes from, and how to write another source
---

# Streams

A decoder does not read a string, it reads a `Stream`. The library ships with `StringStream`, which reads
from a string already in memory:

```php
use CBOR\StringStream;

$stream = StringStream::create($binaryData);
$object = $decoder->decode($stream);
```

A stream is consumed as the document is read, so one stream decodes one document. Several data items
written one after another are read with several `decode()` calls on the same stream.

## Another source

Implement the `Stream` interface to decode from somewhere else — a file, a socket, a buffer filled as it
arrives:

```php
use CBOR\Stream;

class FileStream implements Stream
{
    private $handle;
    private int $position = 0;

    public function __construct(string $filepath)
    {
        $this->handle = fopen($filepath, 'rb');
    }

    public function read(int $length): string
    {
        $data = fread($this->handle, $length);
        $this->position += strlen($data);
        return $data;
    }

    public function getPosition(): int
    {
        return $this->position;
    }

    // … implement the remaining methods
}

// Use it with a decoder
$stream = new FileStream('/path/to/cbor/file.cbor');
$object = $decoder->decode($stream);
```

`read()` is asked for an exact number of bytes and is expected to return them. Returning fewer means the
document ended in the middle of an item, which the decoder reports as an
[error](errors.md): decide there whether to wait for more bytes or to fail.

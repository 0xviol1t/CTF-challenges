# README
There are subtle differences between the local environment and the remote environment. If an attack fails on the remote side, please debug it within the container.

## Build

```
docker build -t chat-with-me .
```

## Run

```
docker run -it --rm --name chat-with-me -p 6666:70 chat-with-me
```

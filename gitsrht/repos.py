import hashlib
import os.path
import subprocess
from gitsrht.types import Artifact, Repository, Redirect
from minio import Minio
from minio.error import BucketAlreadyOwnedByYou, BucketAlreadyExists, ResponseError
from scmsrht.repos import SimpleRepoApi
from srht.config import cfg
from srht.database import db
from werkzeug.utils import secure_filename

repos_path = cfg("git.sr.ht", "repos")
post_update = cfg("git.sr.ht", "post-update-script")

s3_upstream = cfg("objects", "s3-upstream", default=None)
s3_access_key = cfg("objects", "s3-access-key", default=None)
s3_secret_key = cfg("objects", "s3-secret-key", default=None)
s3_bucket = cfg("git.sr.ht", "s3-bucket", default=None)
s3_prefix = cfg("git.sr.ht", "s3-prefix", default=None)

object_storage_enabled = all([
    s3_upstream,
    s3_access_key,
    s3_secret_key,
    s3_bucket,
])

def delete_artifact(artifact):
    minio = Minio(s3_upstream, access_key=s3_access_key,
            secret_key=s3_secret_key, secure=True)
    repo = artifact.repo
    prefix = os.path.join(s3_prefix, "artifacts",
            repo.owner.canonical_name, repo.name)
    try:
        minio.remove_object(s3_bucket, f"{prefix}/{artifact.filename}")
    except ResponseError as err:
        print(err)
    db.session.delete(artifact)

def upload_artifact(valid, repo, commit, f, filename):
    fn = secure_filename(filename)
    artifact = (Artifact.query
            .filter(Artifact.user_id == repo.owner_id)
            .filter(Artifact.repo_id == repo.id)
            .filter(Artifact.commit == commit)
            .filter(Artifact.filename == fn)).one_or_none()
    valid.expect(not artifact, "A file by this name was already uploaded.",
            field="file")
    if not valid.ok:
        return None
    minio = Minio(s3_upstream, access_key=s3_access_key,
            secret_key=s3_secret_key, secure=True)
    prefix = os.path.join(s3_prefix, "artifacts",
            repo.owner.canonical_name, repo.name)
    try:
        minio.make_bucket(s3_bucket)
    except BucketAlreadyOwnedByYou:
        pass
    except BucketAlreadyExists:
        pass
    sha = hashlib.sha256()
    buf = f.read(1024)
    while len(buf) > 0:
        sha.update(buf)
        buf = f.read(1024)
    size = f.tell()
    f.seek(0)
    minio.put_object(s3_bucket, f"{prefix}/{fn}", f, size,
            content_type="application/octet-stream")
    artifact = Artifact()
    artifact.user_id = repo.owner_id
    artifact.repo_id = repo.id
    artifact.commit = commit
    artifact.filename = fn
    artifact.checksum = f"sha256:{sha.hexdigest()}"
    artifact.size = size
    db.session.add(artifact)
    return artifact

class GitRepoApi(SimpleRepoApi):
    def __init__(self):
        super().__init__(repos_path,
                redirect_class=Redirect,
                repository_class=Repository)

    def do_init_repo(self, owner, repo):
        # Note: update gitsrht-shell when changing this
        subprocess.run(["mkdir", "-p", repo.path], check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "init", "--bare"], cwd=repo.path, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "config", "srht.repo-id", str(repo.id)], check=True,
            cwd=repo.path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ln", "-s",
                post_update,
                os.path.join(repo.path, "hooks", "pre-receive")
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ln", "-s",
                post_update,
                os.path.join(repo.path, "hooks", "update")
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ln", "-s",
                post_update,
                os.path.join(repo.path, "hooks", "post-update")
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def do_delete_repo(self, repo):
        from gitsrht.webhooks import RepoWebhook
        RepoWebhook.Subscription.query.filter(
                RepoWebhook.Subscription.repo_id == repo.id).delete()
        # TODO: Should we delete these asyncronously?
        for artifact in (Artifact.query
                .filter(Artifact.user_id == repo.owner_id)
                .filter(Artifact.repo_id == repo.id)):
            delete_artifact(artifact)
        super().do_delete_repo(repo)

    def do_clone_repo(self, source, repo):
        subprocess.run(["mkdir", "-p", repo.path], check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "clone", "--bare", source, repo.path])
        subprocess.run(["git", "config", "srht.repo-id", str(repo.id)], check=True,
            cwd=repo.path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ln", "-s",
                post_update,
                os.path.join(repo.path, "hooks", "update")
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ln", "-s",
                post_update,
                os.path.join(repo.path, "hooks", "post-update")
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
